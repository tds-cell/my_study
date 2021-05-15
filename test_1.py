import decord
import cv2
import mxnet as mx
import pickle
from gluoncv.model_zoo import get_model
from gluoncv.data.transforms.pose import detector_to_alpha_pose, heatmap_to_coord
from gluoncv.utils.viz import cv_plot_keypoints
from gluoncv.data.transforms.presets.ssd import transform_test

#cpuを使う事を明示
ctx = mx.cpu()
video_fname = 'IMG_0031.MOV'
#video_fname = 'IMG_0036.MOV'

vr = decord.VideoReader(video_fname)
#これで<class 'decord.ndarray.NDArray'>を
#<class 'mxnet.ndarray.ndarray.NDArray'>に変換している
decord.bridge.set_bridge('mxnet')
#これは機能している
#<class 'decord.ndarray.NDArray'>の(360, 640, 3)が出力される
#下でエラーになるのでvrの出力をlistに格納したい
#'NDArray' object has no attribute 'tolist'
"""
for i in vr:
    print(i.shape)
    print(type(i))
    print(i)
"""

fps = vr.get_avg_fps()
#print(fps) #30.0

height, width = vr[0].shape[0:2]
#print("height:{}".format(height)) #360
#print("width:{}".format(width))   #640

#コーデックの指定
fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
#出力動画名、コーデック方法等々を規定している
out = cv2.VideoWriter('iwanchu_last_1.mp4',fourcc, fps, (width,height))
#この時点で動画の作成は完了するが中身は空で再生できない

#学習済みデータのダウンロード
detector = get_model('ssd_512_mobilenet1.0_coco', pretrained=True, ctx=ctx, root='./models')
detector.reset_class(classes=['person'], reuse_weights={'person':'person'})
detector.hybridize()

#学習済みデータのダウンロード
estimator = get_model('alpha_pose_resnet101_v1b_coco', pretrained=True, ctx=ctx, root='./models')
estimator.hybridize()

coordinate = []

for each_frame in vr:
    print(each_frame.shape)
    
    x, frame = transform_test(each_frame, short=512)
    class_IDs, scores, bounding_boxs = detector(x.as_in_context(ctx))
    pose_input, upscale_bbox = detector_to_alpha_pose(frame, class_IDs, scores, bounding_boxs)

    if upscale_bbox is not None:
        predicted_heatmap = estimator(pose_input.as_in_context(ctx))
        pred_coords, confidence = heatmap_to_coord(predicted_heatmap, upscale_bbox)
        
        coordinate.append(pred_coords)

        #bounding_boxを表示しないためのダミーデータ
        scores = mx.nd.zeros(shape=(1,100,1))
        
        img = cv_plot_keypoints(frame, pred_coords, confidence, class_IDs, bounding_boxs, scores,
                                box_thresh=0.5, keypoint_thresh=0.2)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        img = cv2.resize(img, (width, height))
        out.write(img)
    else:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(img, (width, height))
        out.write(frame)

with open("coordinate_2.pickle", "wb") as f:
    pickle.dump(coordinate, f)

out.release()


