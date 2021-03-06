from tdw.librarian import ModelLibrarian

librarian = ModelLibrarian()

tables = librarian.get_all_models_in_wnid("n04379243")  # table
TABLE_NAMES = [
    "sm_table_white",
]
TABLES = [record for record in tables if record.name in TABLE_NAMES]

chairs = librarian.get_all_models_in_wnid("n03001627")
CHAIR_NAMES = [
    "emeco_navy_chair",
    "green_side_chair",
    "lapalma_stil_chair",
    "chair_thonet_marshall",
    "wood_chair",
    "chair_billiani_doll",
    "chair_willisau_riale",
    "vitra_meda_chair",
]
CHAIRS = [record for record in chairs if record.name in CHAIR_NAMES]

lamps = librarian.get_all_models_in_wnid("n03367059") # floor lamp
LAMP_NAMES = [
    "alma_floor_lamp",
    "arturoalvarez_v_floor_lamp",
    "b04_kevin_reilly_pattern_floor_lamp",
    "bakerparisfloorlamp03",
    "bastone_floor_lamp",
    "duncan_floor_lamp_crate_and_barrel",
]
LAMPS = [record for record in lamps if record.name in LAMP_NAMES]

# trashbin
# radiator_pub
# pencil_all

drink_names = ["102_pepsi_can_12_fl_oz_vray"]