import os
from datetime import datetime, timedelta
import cv2
import numpy as np
import math

def find_spots_adaptive(image, max_area, min_area, height, width, group_threshold):

    h, w = image.shape[:2]
    ratio = math.floor( h / 4096 )
    text_ratio = h / 4096

    image_blur = cv2.GaussianBlur(image, (1, 1), 0)
    binary_img = cv2.adaptiveThreshold(image_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 301, 30)
    binary_img = cv2.dilate(binary_img, None, iterations=1)
    binary_img = cv2.erode(binary_img, None, iterations=1)
    _, _, boxes, centroid = cv2.connectedComponentsWithStats(binary_img)
    boxes = boxes[1:]
    filtered_boxes = []
    filtered_centroid = []
    for (x, y, w, h, pixels), cent in zip(boxes, centroid):
        if pixels < max_area and pixels > min_area and h > height and w > width:
            filtered_boxes.append((x, y, w, h))
            filtered_centroid.append(cent)

    im_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    oversize = 4
    total_sunspots = 0
    sunspot_groups = []

    for i, (x, y, w, h) in enumerate(filtered_boxes):
        total_sunspots += 1
        cv2.rectangle(im_rgb, (x - oversize, y - oversize), (x + w + oversize, y + h + oversize), (255, 0, 0),
                      2 * ratio)

    #threshold=290 threshold=257.8 threshold=284 #threshold=279.5
    grouped_boxes = group_boxes(filtered_boxes, threshold=group_threshold)
    print(f"Total big boxes: {len(grouped_boxes)}")

    for i, (x, y, w, h) in enumerate(grouped_boxes):
        group_sunspots = sum(1 for bx, by, bw, bh in filtered_boxes if x <= bx <= x + w and y <= by <= y + h)
        sunspot_groups.append({
            'Group': i,
            'Sunspots': group_sunspots
        })

        cv2.rectangle(im_rgb, (x, y), (x + w, y + h), (0, 255, 0), 4 * ratio)

        cv2.putText(im_rgb, f'Box {i}', (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 2.5 * text_ratio, (0, 0, 255), 2 * ratio, cv2.LINE_AA)

        box_sunspots = sum(1 for bx, by, bw, bh in filtered_boxes if x <= bx <= x + w and y <= by <= y + h)

        cv2.putText(im_rgb, f'Sunspots: {box_sunspots}', (x, y - 60), cv2.FONT_HERSHEY_SIMPLEX, 2.5 * text_ratio, (0, 0, 255), 2 * ratio,cv2.LINE_AA)

        cv2.putText(im_rgb, f'{len(filtered_boxes)}', (100, 400), cv2.FONT_HERSHEY_SIMPLEX, 12 * text_ratio, (0, 255, 0), 10 * ratio, cv2.LINE_AA)


    return im_rgb, sunspot_groups, total_sunspots, len(grouped_boxes), grouped_boxes


def group_boxes(boxes, threshold):

    grouped_boxes = []
    used = set()
    for i, box1 in enumerate(boxes):
        if i not in used:
            grouped_box = list(box1)
            for j, box2 in enumerate(boxes):
                if i != j and calculate_distance(box1, box2) < threshold:
                    if j not in used:
                        x = min(grouped_box[0], box2[0])
                        y = min(grouped_box[1], box2[1])
                        xw = max(grouped_box[0] + grouped_box[2] - x, box2[0] + box2[2] - x, 0)
                        yw = max(grouped_box[1] + grouped_box[3] - y, box2[1] + box2[3] - y, 0)
                        grouped_box[0], grouped_box[1], grouped_box[2], grouped_box[3] = x, y, xw, yw
                        used.add(j)
            grouped_boxes.append(grouped_box)

    return grouped_boxes

def calculate_distance(box1, box2):
    x1, y1, _, _ = box1
    x2, y2, _, _ = box2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def Hough(image, param1, param2, thickness):

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray_image, 1, 255, cv2.THRESH_BINARY)
    mask = np.zeros_like(binary_image)
    cv2.circle(mask, (mask.shape[1] // 2, mask.shape[0] // 2), min(mask.shape) // 2, 255,
               -1)

    masked_binary_image = cv2.bitwise_and(binary_image, mask)
    nonzero_points = np.nonzero(masked_binary_image)
    min_x = np.min(nonzero_points[1])
    max_x = np.max(nonzero_points[1])
    min_y = np.min(nonzero_points[0])
    max_y = np.max(nonzero_points[0])
    x = min_x
    y = min_y
    width = max_x - min_x
    height = max_y - min_y

    mean = int((width + height) / 2)
    radius = int(mean / 2)

    if abs(width-height) != 0:
        if abs(width-height) >= 3:
            radius = radius + int(abs(width-height) / 3)
        else:
            radius = radius + int(abs(width - height))

    cv2.rectangle(image, (x, y), (x + width, y + height), (0, 255, 0), thickness)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 30, 150)
    #param1=25 #param2=15
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1, minDist=1,
                               param1=param1, param2=param2, minRadius=0, maxRadius=radius)

    return circles, radius, thickness


def contours(image):

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray_image, 1, 255, cv2.THRESH_BINARY)
    mask = np.zeros_like(binary_image)
    cv2.circle(mask, (mask.shape[1] // 2, mask.shape[0] // 2), min(mask.shape) // 2, 255,
               -1)
    masked_binary_image = cv2.bitwise_and(binary_image, mask)

    nonzero_points = np.nonzero(masked_binary_image)
    min_x = np.min(nonzero_points[1])
    max_x = np.max(nonzero_points[1])
    min_y = np.min(nonzero_points[0])
    max_y = np.max(nonzero_points[0])
    width = max_x - min_x
    height = max_y - min_y
    mean = int((width + height) / 2)
    radius = int(mean / 2)
    contours, _ = cv2.findContours(masked_binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        print("Error: No contours found.")
        return None, None

    max_contour = max(contours, key=cv2.contourArea)
    x, y, width, height = cv2.boundingRect(max_contour)
    segmented_image = image.copy()
    cv2.rectangle(segmented_image, (x, y), (x + width, y + height), (0, 0, 255), 5)
    (center_x, center_y), radius = cv2.minEnclosingCircle(max_contour)
    center = (int(center_x), int(center_y))
    radius = int(radius)
    cv2.circle(segmented_image, center, radius, (0, 255, 0), 5)

    return segmented_image, radius


def adjust_params_by_radius(radius, reference_radius, params):

    scaling_factor = radius / reference_radius
    adjusted_params = [int(param * scaling_factor) for param in params]

    return adjusted_params

def find_spots_with_adjusted_params(gray_image, radius, reference_radius, original_params):

    adjusted_params = adjust_params_by_radius(radius, reference_radius, original_params)
    spots_image, groups, total_sunspots, nr_of_groups, grouped_boxes = find_spots_adaptive(gray_image, *adjusted_params)

    return spots_image, groups, total_sunspots, nr_of_groups, grouped_boxes

def adjust_hough_params(image, original_params, new_resolution):

    original_rez, original_param1, original_param2, original_thickness = original_params
    resolution_ratio = new_resolution / original_rez
    adjusted_params = [
        round(original_param1 * resolution_ratio),
        round(original_param2 * resolution_ratio),
        round(original_thickness * resolution_ratio)
    ]

    return Hough(image, adjusted_params[0],adjusted_params[1],adjusted_params[2])

reference_radius = 1938
original_params = [10000, 30, 5, 5, 279.5]  #image, max_area, min_area, height, width, group_threshold
#threshold=290 threshold=257.8 threshold=284 #threshold=279.5

original_Hough_params = [4096, 50, 30, 10] #rez, par1 par2, thickenss


def return_sunspots_image(image):

    height, width = image.shape[:2]
    circles, radius, thickness = adjust_hough_params(image, original_Hough_params, height)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    spots_image, groups, total_sunspots, nr_of_groups, grouped_boxes = find_spots_with_adjusted_params(gray_image, radius, reference_radius, original_params)
    if circles is not None:
            circles = circles.round().astype("int")
            max_circle = max(circles[0, :], key=lambda x: x[2])
            x, y, r = max_circle
            cv2.circle(spots_image, (x, y), r, (255, 156, 0), thickness+2)

    return spots_image, groups, total_sunspots, nr_of_groups, grouped_boxes
