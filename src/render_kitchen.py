import numpy as np
from json import loads
from pathlib import Path
from typing import List
from tdw.tdw_utils import TDWUtils
from platform import system
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.interior_scene_lighting import InteriorSceneLighting
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.backend.platforms import SYSTEM_TO_S3

# https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/photorealism/interior_scene.py
class InteriorScene(Controller):
    """
    Load an interior scene populated with objects. Render images of the scene using each interior lighting HDRI skybox.
    """

    def __init__(
        self, port: int = 1071, check_version: bool = True, launch_build: bool = True
    ):
        super().__init__(
            port=port, check_version=check_version, launch_build=launch_build
        )
        self.communicate({"$type": "set_screen_size", "width": 1024, "height": 768})
        # Load the commands used to initialize the objects in the scene.
        init_commands_text = Path("src\interior_scene.json").read_text()
        # Replace the URL platform infix.
        init_commands_text = init_commands_text.replace(
            "/windows/", "/" + SYSTEM_TO_S3[system()] + "/"
        )
        # Load the commands as a list of dictionaries.
        self.init_commands = loads(init_commands_text)
        # Set the camera. The position and rotation of the camera doesn't change between scenes.
        self.camera: ThirdPersonCamera = ThirdPersonCamera(
            avatar_id="a",
            position={"x": -0.6771, "y": 2, "z": 2.0463},
            look_at={"x": 0.1, "y": 0, "z": -0.1},
        )
        # Enable image capture.
        self.path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("interior_scene")
        self.depth_output = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath(
            "interior_scene/output.npy"
        )
        print(f"Images will be saved to: {self.path}")
        self.capture: ImageCapture = ImageCapture(
            avatar_ids=["a"], path=self.path, pass_masks=["_img", "_id", "_depth"]
        )
        # Create the scene lighting add-on.
        self.interior_scene_lighting = InteriorSceneLighting()
        # Append the add-ons.
        self.add_ons.extend([self.interior_scene_lighting, self.camera, self.capture])
        # Get a list of HDRI skybox names.
        self.hdri_skybox_names = list(
            InteriorSceneLighting.SKYBOX_NAMES_AND_POST_EXPOSURE_VALUES.keys()
        )
        self.depth_value_dump: List[np.array] = list()

    def show_skybox(self, hdri_skybox_index: int) -> None:
        # Reset the add-ons.
        self.camera.initialized = False
        self.capture.initialized = False
        # Set the next HDRI skybox.
        self.interior_scene_lighting.reset(
            hdri_skybox=self.hdri_skybox_names[hdri_skybox_index]
        )
        # Load the scene, populate with objects, add the camera, set the skybox and post-processing, and capture an image.
        self.communicate(self.init_commands)
        # Rename the image to the name of the skybox.
        src_filename = "a/img_" + str(self.capture.frame - 1).zfill(4) + ".jpg"
        dst_filename = "a/" + self.hdri_skybox_names[hdri_skybox_index] + ".jpg"
        self.path.joinpath(src_filename).replace(self.path.joinpath(dst_filename))
        self.images = self.capture.images["a"]
        for i in range(self.images.get_num_passes()):
            if self.images.get_pass_mask(i) == "_depth":
                depth_values = TDWUtils.get_depth_values(
                    self.images.get_image(i),
                    depth_pass="_depth",
                    width=self.images.get_width(),
                    height=self.images.get_height(),
                )
                self.depth_value_dump.append(depth_values)

    def show_all_skyboxes(self) -> None:
        self.show_skybox(hdri_skybox_index=3)
        np.save(str(self.depth_output.resolve())[:-4], np.array(self.depth_value_dump))
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = InteriorScene()
    c.show_all_skyboxes()
