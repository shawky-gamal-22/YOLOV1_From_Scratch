import torch
from collections import Counter 




def intersection_over_union(boxes_preds, boxe_labels, box_format="mindpoint"):
    """
    Calculates the intersection over union

    Parameters:
        boxes_preds (tensor): Predictions of Bounding Boxes (BATCH_SIZE, 4)
        boxes_labels (tensor): Correct labels of Bounding Boxes (BATCH_SIZE, 4)
        box_format (str): midpoint/corners, if boxes (x,y,w,h) or (x1,y1,x2,y2)

    Returns:
        tensor: Intersection over union for all examples
    """
    if box_format == "mindpoint":
        box1_x1 = boxes_preds[..., 0:1] - boxes_preds[..., 2:3] / 2
        box1_y1 = boxes_preds[..., 1:2] - boxes_preds[..., 3:4] / 2
        box1_x2 = boxes_preds[..., 0:1] + boxes_preds[..., 2:3] / 2
        box1_y2 = boxes_preds[..., 1:2] + boxes_preds[..., 3:4] / 2
        box2_x1 = boxe_labels[..., 0:1] - boxe_labels[..., 2:3] / 2
        box2_y1 = boxe_labels[..., 1:2] - boxe_labels[..., 3:4] / 2
        box2_x2 = boxe_labels[..., 0:1] + boxe_labels[..., 2:3] / 2
        box2_y2 = boxe_labels[..., 1:2] + boxe_labels[..., 3:4] / 2

    if box_format == "corners":
        box1_x1 = boxes_preds[..., 0:1]
        box1_y1 = boxes_preds[..., 1:2]
        box1_x2 = boxes_preds[..., 2:3]
        box1_y2 = boxes_preds[..., 3:4] # (N,1) 
        box2_x1 = boxe_labels[..., 0:1]
        box2_y1 = boxe_labels[..., 1:2]
        box2_x2 = boxe_labels[..., 2:3]
        box2_y2 = boxe_labels[..., 3:4] # (N,1) 



    x1 = torch.max(box1_x1, box2_x1)
    y1 = torch.max(box1_y1, box2_y1)
    x2 = torch.max(box1_x2, box2_x2)
    y2 = torch.max(box1_y2, box2_y2)

    # .clamp(0) is for the case when the intersection is negative or do not intersect
    intersection = (x2 - x1).clamp(0)  * (y2 - y1).clamp(0)

    box1_area = abs((box1_x2 - box1_x1) * (box1_y2 - box1_y1))
    box2_area = abs((box2_x2 - box2_x1) * (box2_y2 - box2_y1))

    return intersection / (box1_area + box2_area - intersection + 1e-6)




def mean_average_precision(
        pred_boxes,
        true_boxes,
        iou_threshold=0.5,
        box_format = 'corners',
        num_classes = 20):
    
    """
    Calculates the mean average precision (mAP) for object detection.
    
        Args:
        pred_boxes (list): List of predicted bounding boxes with each box represented as 
                   [train_idx, class_pred, prob_score, x1, y1, x2, y2].
        true_boxes (list): List of ground truth bounding boxes with each box represented as 
                   [train_idx, class_label, x1, y1, x2, y2].
        iou_threshold (float, optional): Intersection over Union (IoU) threshold to consider a detection as True Positive. Default is 0.5.
        box_format (str, optional): Format of the bounding boxes. Either 'corners' (x1, y1, x2, y2) or 'midpoint' (x, y, width, height). Default is 'corners'.
        num_classes (int, optional): Number of classes. Default is 20.

        Returns:
        float: The mean average precision (mAP) value.
    
    """

    # pred_boxes (list) : [[train_idx, class_pred, prob_score, x1, y1, x2, y2], ...]
    average_precisions = []
    epsilon = 1e-6

    for c in range(num_classes):

        detections = []
        ground_truths = []

        for detection in pred_boxes:
            if detection[1] == c:
                detections.append(detection) # if class is c, append to detections
    
        for true_box in true_boxes:
            if true_box[1] == c:
                ground_truths.append(true_box) # if class is c, append to ground_truths

        # img 0 has 3 bboxes
        # img 1 has 5 bboxes
        # amount_bboxes = {0:3, 1:5}
        amount_bboxes = Counter([gt[0] for gt in ground_truths]) # amount of ground truth boxes

        for key, val in amount_bboxes.items():
            amount_bboxes[key] = torch.zeros(val) # tensor([0, 0, 0, 0, 0]) for example
            # amount_bboxes = {0:tensor([0, 0, 0]), 1:tensor([0, 0, 0, 0, 0])}

        detection.sort(key=lambda x: x[2], reverse=True) # sort by prob_score
        TP = torch.zeros((len(detections))) # create tensor for True Positives
        FP = torch.zeros((len(detections))) # create tensor for False Positives
        total_true_bboxes = len(ground_truths)

        for detection_idx, detection in enumerate(detections):
            ground_truth_img = [
                bbox for bbox in ground_truths if bbox[0] == detection[0]
            ]

            num_gts = len(ground_truth_img)
            best_iou = 0

            for idx, gt in enumerate(ground_truth_img):
                iou = intersection_over_union(
                    torch.tensor(detection[3:]),
                    torch.tensor(gt[3:]),
                    box_format = box_format
                )

                if iou > best_iou:
                    best_iou = iou
                    best_gt_idx = idx

            if best_iou > iou_threshold:
                if amount_bboxes[detection[0]][best_gt_idx] == 0:
                    TP[detection_idx] = 1
                    amount_bboxes[detection[0]][best_gt_idx] = 1
                else:
                    FP[detection_idx] = 1
            else:
                FP[detection_idx] = 1
        # [1, 1, 0, 1, 0] -> [1, 2, 2, 3, 3]
        TP_cumsum = torch.cumsum(TP, dim=0)
        FP_cumsum = torch.cumsum(FP, dim=0)

        recalls = TP_cumsum / (total_true_bboxes + epsilon)
        precisions = torch.divide(TP_cumsum, (TP_cumsum + FP_cumsum + epsilon))
        precisions = torch.cat((torch.tensor([1]), precisions))
        recalls = torch.cat((torch.tensor([0]), recalls))
        average_precisions.append(torch.trapz(precisions, recalls))

    return sum(average_precisions) / len(average_precisions)






def nms(
        bboxes,
        iou_threshold,
        threshold,
        box_format="corners"):
    
    """
    Non-Max Suppression Algorithm
    1. Sort all the predictions by their probabilities
    2. Select the prediction with the highest probability
    3. Remove all the predictions with IoU > threshold with the selected prediction
    4. Repeat step 2 and 3 until there are no more predictions left
    5. Output the selected predictions

    Parameters:
        1. bboxes (list): [[1, 0.9, x1, y1, x2, y2], [1, 0.75, x1, y1, x2, y2], ...]
        2. iou_threshold (float): IoU threshold for removing the boxes
        3. threshold (float): Threshold for the probability of the boxes
        4. box_format (str): "midpoint" or "corners" used to specify the format of the boxes

    Returns:
        1. list: Selected boxes after performing non-max suppression

"""
    
    # predictions = [[1(class number), 0.9-> probability, x1,y1,x2,y2], [], []]
    
    assert type(bboxes) == list

    boxess = [box for box in bboxes if box[1] > threshold]
    bboxes = sorted(bboxes, key= lambda x: x[1], reverse=True)
    boxess_after_nms = []


    while bboxes:
        chosen_box = bboxes.pop(0)

        bboxes = [
            box 
            for box in bboxes
            if box[0] != chosen_box[0]
            or intersection_over_union(
                torch.tensor(chosen_box[2:]),
                torch.tensor(box[2:]),
                box_format= box_format
            ) > iou_threshold
        ]

        boxess_after_nms.append(chosen_box)

        return boxess_after_nms