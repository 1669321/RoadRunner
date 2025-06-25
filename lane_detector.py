import cv2
import numpy as np

def abs_sobel_thresh(img, orient='x', thresh_min=20, thresh_max=100):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if orient == 'x':
        sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
    else:
        sobel = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
    abs_sobel = np.absolute(sobel)
    scaled = np.uint8(255 * abs_sobel / np.max(abs_sobel))
    binary_output = np.zeros_like(scaled)
    binary_output[(scaled >= thresh_min) & (scaled <= thresh_max)] = 1
    return binary_output

def color_threshold(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Detectar líneas amarillas
    lower_yellow = np.array([15, 100, 100])
    upper_yellow = np.array([35, 255, 255])
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Detectar líneas blancas
    sensitivity = 68
    lower_white = np.array([0, 0, 255 - sensitivity])
    upper_white = np.array([255, sensitivity, 255])
    white_mask = cv2.inRange(hsv, lower_white, upper_white)

    combined = cv2.bitwise_or(yellow_mask, white_mask)
    return combined

def combined_threshold(img):
    sobel_binary = abs_sobel_thresh(img, orient='x', thresh_min=20, thresh_max=100)
    color_binary = color_threshold(img)
    combined = np.zeros_like(sobel_binary)
    combined[(sobel_binary == 1) | (color_binary > 0)] = 1
    return combined

def warp_perspective(img):
    h, w = img.shape[:2]
    src = np.float32([[w*0.45, h*0.63],
                      [w*0.55, h*0.63],
                      [w*0.9, h*0.95],
                      [w*0.1, h*0.95]])
    dst = np.float32([[w*0.2, 0],
                      [w*0.8, 0],
                      [w*0.8, h],
                      [w*0.2, h]])
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)
    return warped, M

def find_lane_pixels(binary_warped):
    histogram = np.sum(binary_warped[binary_warped.shape[0]//2:,:], axis=0)
    midpoint = histogram.shape[0]//2
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    # Número de ventanas
    nwindows = 9
    window_height = binary_warped.shape[0] // nwindows
    nonzero = binary_warped.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])

    margin = 100
    minpix = 50

    leftx_current = leftx_base
    rightx_current = rightx_base

    left_lane_inds = []
    right_lane_inds = []

    for window in range(nwindows):
        win_y_low = binary_warped.shape[0] - (window+1)*window_height
        win_y_high = binary_warped.shape[0] - window*window_height

        win_xleft_low = leftx_current - margin
        win_xleft_high = leftx_current + margin

        win_xright_low = rightx_current - margin
        win_xright_high = rightx_current + margin

        good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                          (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
        good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                           (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]

        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)

        if len(good_left_inds) > minpix:
            leftx_current = int(np.mean(nonzerox[good_left_inds]))
        if len(good_right_inds) > minpix:
            rightx_current = int(np.mean(nonzerox[good_right_inds]))

    left_lane_inds = np.concatenate(left_lane_inds)
    right_lane_inds = np.concatenate(right_lane_inds)

    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]

    return leftx, lefty, rightx, righty

def fit_polynomial(binary_warped):
    leftx, lefty, rightx, righty = find_lane_pixels(binary_warped)
    left_fit = np.polyfit(lefty, leftx, 2) if len(leftx) > 0 else None
    right_fit = np.polyfit(righty, rightx, 2) if len(rightx) > 0 else None
    return left_fit, right_fit

def draw_lane(original_img, binary_warped, left_fit, right_fit, Minv):
    h, w = original_img.shape[:2]
    ploty = np.linspace(0, h-1, h)
    color_warp = np.zeros_like(original_img).astype(np.uint8)

    if left_fit is not None and right_fit is not None:
        left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
        right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]

        pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
        pts = np.hstack((pts_left, pts_right))

        cv2.fillPoly(color_warp, np.int_([pts]), (0,255,0))

    newwarp = cv2.warpPerspective(color_warp, Minv, (w, h))
    result = cv2.addWeighted(original_img, 1, newwarp, 0.3, 0)
    return result

def lane_detector_pipeline(image):
    combined = combined_threshold(image)
    warped, M = warp_perspective(combined)
    Minv = cv2.getPerspectiveTransform(np.float32([[image.shape[1]*0.45, image.shape[0]*0.63],
                                                   [image.shape[1]*0.55, image.shape[0]*0.63],
                                                   [image.shape[1]*0.9, image.shape[0]*0.95],
                                                   [image.shape[1]*0.1, image.shape[0]*0.95]]),
                                      np.float32([[image.shape[1]*0.2, 0],
                                                  [image.shape[1]*0.8, 0],
                                                  [image.shape[1]*0.8, image.shape[0]],
                                                  [image.shape[1]*0.2, image.shape[0]]]))
    left_fit, right_fit = fit_polynomial(warped)
    output = draw_lane(image, warped, left_fit, right_fit, Minv)
    
    # Convertir la imagen binarizada warped a formato 3 canales para mostrar
    binarized_vis = (warped * 255).astype(np.uint8)
    binarized_vis = cv2.cvtColor(binarized_vis, cv2.COLOR_GRAY2BGR)
    
    return output, binarized_vis


if __name__ == "__main__":
    cap = cv2.VideoCapture("./videos/vid1.mp4")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        lane_img, binary_img = lane_detector_pipeline(frame)
        
        cv2.imshow("Lane Detector", lane_img)
        cv2.imshow("Binarized Filter", binary_img)  # <-- Mostrar la binarizada
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

