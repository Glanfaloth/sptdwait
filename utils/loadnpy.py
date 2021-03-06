import numpy as np
import os
import argparse
import matplotlib.pyplot as plt
from tdw.tdw_utils import TDWUtils
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
parser = argparse.ArgumentParser(description="which scene")
parser.add_argument("--scene", default="scene_office")
parser.add_argument("--name", default="vr")
args = parser.parse_args()
data = np.load(EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath(args.scene + "/" + args.name + ".npy"))
for i in range(len(data)):
    print(i)
    path = os.path.join(
                        EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath( args.scene),
                        args.name,
                        "depth_value_" + TDWUtils.zero_padding(i, 4) + ".png",
                    )
    plt.imshow(data[i])
    plt.savefig(path)
    plt.close()