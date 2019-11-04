import os
import sys
import darknet


class Detector:

    def __init__(self):
        # initialize darknet NN
        self.meta_main = None
        self.net_main = None
        self.alt_names = None

        config_path = "cfg/yolov3-tiny-obj.cfg"
        weight_path = "backup/yolov3-tiny-obj_2000.weights"
        meta_path = "data/r2d2.data"

        if self.net_main is None:
            self.net_main = darknet.load_net_custom(config_path.encode("ascii"), weight_path.encode("ascii"), 0, 1)  # batch size = 1
        if self.meta_main is None:
            self.meta_main = darknet.load_meta(meta_path.encode("ascii"))
        if self.alt_names is None:
            try:
                with open(meta_path) as metaFH:
                    meta_contents = metaFH.read()
                    import re
                    match = re.search("names *= *(.*)$", meta_contents,
                                      re.IGNORECASE | re.MULTILINE)
                    if match:
                        result = match.group(1)
                    else:
                        result = None
                    try:
                        if os.path.exists(result):
                            with open(result) as namesFH:
                                names_list = namesFH.read().strip().split("\n")
                                self.alt_names = [x.strip() for x in names_list]
                    except TypeError:
                        pass
            except Exception:
                pass

        self.darknet_image = darknet.make_image(darknet.network_width(self.net_main),
                                                darknet.network_height(self.net_main), 3)

        self.thresh = 0.25

    def detect(self, image):
        darknet.copy_image_from_bytes(self.darknet_image, image.tobytes())
        detections = darknet.detect_image(self.net_main, self.meta_main, self.darknet_image, thresh=self.thresh)
        return detections

    def get_network_size(self):
        size = (darknet.network_width(self.net_main), darknet.network_height(self.net_main))
        return size

