import numpy as np
import random
import argparse
import constants
from typing import List
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_touch import OculusTouch
from tdw.vr_data.oculus_touch_button import OculusTouchButton
from tdw.librarian import ModelLibrarian
from tdw.output_data import Bounds
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

parser = argparse.ArgumentParser(description="add obj")
parser.add_argument("--cup", default="cup")
parser.add_argument("--fruit", default="none")
parser.add_argument("--book", default="none")
parser.add_argument("--pen", default="none")
args = parser.parse_args()


class OculusTouchOfficeScene(Controller):
    librarian = ModelLibrarian()

    TABLES = constants.TABLES
    CHAIRS = constants.CHAIRS
    LAMPS = constants.LAMPS

    def __init__(
        self, port: int = 1071, check_version: bool = True, launch_build: bool = True
    ):
        super().__init__(
            port=port, check_version=check_version, launch_build=launch_build
        )
        self.simulation_done = False
        self.trial_done = False
        self.vr = OculusTouch(set_graspable=False, attach_avatar=True)
        # Quit when the left trigger button is pressed.
        self.vr.listen_to_button(
            button=OculusTouchButton.trigger_button, is_left=True, function=self.quit
        )
        # End the trial when the right trigger button is pressed.
        self.vr.listen_to_button(
            button=OculusTouchButton.trigger_button,
            is_left=False,
            function=self.end_trial,
        )
        self.add_ons.extend([self.vr])
        self.path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("scene_office")
        self.depth_output = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath(
            "scene_office/output.npy"
        )
        self.communicate(
            [
                TDWUtils.create_empty_room(12, 12),
                {"$type": "set_render_quality", "render_quality": 0},
            ]
        )
        self.capture = ImageCapture(
            path=self.path, avatar_ids=["vr"], pass_masks=["_img", "_id", "_depth"]
        )
        self.add_ons.append(self.capture)

    def get_chair_position(
        self, table_center: np.array, table_bound_point: np.array
    ) -> np.array:
        position_to_center = table_bound_point - table_center
        position_to_center_normalized = position_to_center / np.linalg.norm(
            position_to_center
        )
        chair_position = table_bound_point + (
            position_to_center_normalized * random.uniform(1, 0.25)
        )
        chair_position[1] = 0
        return chair_position

    def trial(self) -> None:
        self.vr.reset()
        # Start a new trial.
        self.trial_done = False
        # Choose a random model.
        table = random.choice(OculusTouchOfficeScene.TABLES)
        chair = random.choice(OculusTouchOfficeScene.CHAIRS)
        lamp = random.choice(OculusTouchOfficeScene.LAMPS)
        table_x = 0
        table_z = 0.5
        table_id = self.get_unique_id()
        # Add the model.
        resp = self.communicate(
            [
                {
                    "$type": "add_object",
                    "name": table.name,
                    "url": "https://tdw-public.s3.amazonaws.com/models/windows/2018-2019.1/"
                    + table.name,
                    "scale_factor": 1.0,
                    "position": {"x": table_x, "y": 0, "z": table_z},
                    "category": "table",
                    "id": table_id,
                },
                {
                    "$type": "rotate_object_to_euler_angles",
                    "euler_angles": {"x": 0, "y": 0, "z": 0},
                    "id": table_id,
                },
                {
                    "$type": "set_kinematic_state",
                    "id": table_id,
                    "is_kinematic": True,  # kinematic object is non-graspable
                    "use_gravity": True,
                },
                {"$type": "set_mass", "mass": 50, "id": table_id},
                {
                    "$type": "set_physic_material",
                    "dynamic_friction": 0.45,
                    "static_friction": 0.48,
                    "bounciness": 0.5,
                    "id": table_id,
                },
                {"$type": "send_bounds", "frequency": "once", "ids": [table_id]},
            ]
        )

        bounds = Bounds(resp[0])
        table_center = np.array(bounds.get_center(0))
        table_left = np.array(bounds.get_left(0))
        table_right = np.array(bounds.get_right(0))
        table_top = bounds.get_top(0)
        table_bottom = TDWUtils.array_to_vector3(bounds.get_bottom(0))
        chair_positions = [
            self.get_chair_position(
                table_center=table_center,
                table_bound_point=table_left,
            ),
            self.get_chair_position(
                table_center=table_center,
                table_bound_point=table_right,
            ),
        ]
        cup_id = self.get_unique_id()
        computer_id = self.get_unique_id()
        mouse_id = self.get_unique_id()
        lamp_id = self.get_unique_id()
        fruit_id = self.get_unique_id()
        book_id = self.get_unique_id()
        pen_id = self.get_unique_id()
        self.communicate(
            [
                self.get_add_object(
                    model_name="macbook_air",
                    object_id=computer_id,
                    position={
                        "x": table_x + 0.1,
                        "y": table_top[1],
                        "z": table_z + 0.3,
                    },
                    rotation={"x": 0, "y": 180, "z": 0},
                ),
                self.get_add_object(
                    model_name="mouse_02_vray",
                    object_id=mouse_id,
                    position={
                        "x": table_x + 0.4,
                        "y": table_top[1],
                        "z": table_z + 0.2,
                    },
                    rotation={"x": 0, "y": 0, "z": 0},
                ),
                self.get_add_object(
                    model_name=lamp.name,
                    object_id=lamp_id,
                    position={
                        "x": table_left[0] - 0.3,
                        "y": 0,
                        "z": table_left[2] + 1,
                    },
                    rotation={"x": 0, "y": 180, "z": 0},
                ),
                self.get_add_object(
                    model_name=args.cup,
                    object_id=cup_id,
                    position={
                        "x": table_x - 0.3,
                        "y": table_top[1],
                        "z": table_z - 0.3,
                    },
                    rotation={"x": 0, "y": 0, "z": 0},
                ),
            ]
        )
        if args.fruit != "none":
            self.communicate(
                self.get_add_object(
                    model_name=args.fruit,
                    object_id=fruit_id,
                    position={
                        "x": table_x - 0.3,
                        "y": table_top[1],
                        "z": table_z + 0.1,
                    },
                    rotation={"x": 0, "y": 0, "z": 0},
                ),
            )
        if args.book != "none":
            self.communicate(
                self.get_add_object(
                    model_name=args.book,
                    object_id=book_id,
                    position={
                        "x": table_x,
                        "y": table_top[1],
                        "z": table_z - 0.2,
                    },
                    rotation={"x": 0, "y": random.uniform(-360, 360), "z": 0},
                ),
            )
        if args.pen != "none":
            self.communicate(
                self.get_add_object(
                    model_name=args.pen,
                    object_id=pen_id,
                    position={
                        "x": table_x + 0.3,
                        "y": table_top[1],
                        "z": table_z - 0.2,
                    },
                    rotation={"x": 0, "y": random.uniform(-360, 360), "z": 0},
                ),
            )
        commands = []
        chair_ids = []
        for chair_position in chair_positions:
            object_id = self.get_unique_id()
            chair_ids.append(object_id)
            commands.extend(
                self.get_add_physics_object(
                    model_name=chair.name,
                    position=TDWUtils.array_to_vector3(chair_position),
                    object_id=object_id,
                ),
            )
            commands.extend(
                [
                    {
                        "$type": "object_look_at_position",
                        "position": table_bottom,
                        "id": object_id,
                    },
                    {
                        "$type": "rotate_object_by",
                        "angle": float(random.uniform(-20, 20)),
                        "id": object_id,
                        "axis": "yaw",
                    },
                ]
            )

        self.communicate(commands)

        self.depth_value_dump: List[np.array] = list()

        # Wait until the trial is done.
        while not self.trial_done and not self.simulation_done:
            self.images = self.capture.images["vr"]
            for i in range(self.images.get_num_passes()):
                if self.images.get_pass_mask(i) == "_depth":
                    # Get the depth values.
                    depth_values = TDWUtils.get_depth_values(
                        self.images.get_image(i),
                        depth_pass="_depth",
                        width=self.images.get_width(),
                        height=self.images.get_height(),
                    )
                    self.depth_value_dump.append(depth_values)
            self.communicate([])
        # Destroy the object.
        self.communicate(
            [
                {"$type": "destroy_object", "id": table_id},
                {"$type": "destroy_object", "id": cup_id},
                {"$type": "destroy_object", "id": computer_id},
                {"$type": "destroy_object", "id": mouse_id},
                {"$type": "destroy_object", "id": lamp_id},
                {"$type": "destroy_object", "id": fruit_id},
                {"$type": "destroy_object", "id": book_id},
                {"$type": "destroy_object", "id": pen_id},
            ]
        )
        for chair_id in chair_ids:
            self.communicate(
                {"$type": "destroy_object", "id": chair_id},
            )

    def run(self) -> None:
        while not self.simulation_done:
            # Run a trial.
            self.trial()
        # End the simulation.
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.simulation_done = True
        np.save(str(self.depth_output.resolve())[:-4], np.array(self.depth_value_dump))

    def end_trial(self):
        self.trial_done = True


if __name__ == "__main__":
    c = OculusTouchOfficeScene()
    c.run()
