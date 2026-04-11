from models.house_owner import HouseOwner
from models.house_seeker import HouseSeeker

# --- House Owners ---

egle = HouseOwner(
    user_id=1,
    name="Eglė",
    age=24,
    gender="female",
    occupation="Artist",
    bio="Loves quiet mornings and painting.",
    avatar_url="",
    habits=["Quiet", "Non-smoker", "Clean", "Creative", "Early riser"],
    languages=["Lithuanian", "English"],
    neighborhood="Užupis",
    monthly_rent=600,
)

matas = HouseOwner(
    user_id=2,
    name="Matas",
    age=26,
    gender="male",
    occupation="Software Developer",
    bio="Tech enthusiast looking for a tidy roommate.",
    avatar_url="",
    habits=["Clean", "Work from home", "Non-smoker", "Quiet", "Friendly"],
    languages=["Lithuanian", "English"],
    neighborhood="Šnipiškės",
    monthly_rent=750,
)

lukas = HouseOwner(
    user_id=3,
    name="Lukas",
    age=28,
    gender="male",
    occupation="Chef",
    bio="Loves cooking for friends.",
    avatar_url="",
    habits=["Night owl", "Foodie", "Social", "Friendly", "Non-smoker"],
    languages=["Lithuanian"],
    neighborhood="Naujamiestis",
    monthly_rent=550,
)

# --- House Seekers ---

ieva = HouseSeeker(
    user_id=4,
    name="Ieva",
    age=22,
    gender="female",
    occupation="Student",
    bio="Looking for a central place to stay.",
    avatar_url="",
    habits=["Social", "Early bird", "Friendly", "Clean", "Non-smoker"],
    languages=["Lithuanian", "English"],
    max_budget=500,
    preferred_neighborhoods=["Senamiestis", "Naujamiestis"],
)

domas = HouseSeeker(
    user_id=5,
    name="Domas",
    age=25,
    gender="male",
    occupation="Engineer",
    bio="Moving to Vilnius for a new job.",
    avatar_url="",
    habits=["Quiet", "Non-smoker", "Clean", "Work from home", "Friendly"],
    languages=["Lithuanian", "English"],
    max_budget=700,
    preferred_neighborhoods=["Žvėrynas", "Šnipiškės"],
)

austeja = HouseSeeker(
    user_id=6,
    name="Austėja",
    age=23,
    gender="female",
    occupation="Designer",
    bio="Looking for a bright room with a balcony.",
    avatar_url="",
    habits=["Pet friendly", "Creative", "Non-smoker", "Clean", "Early riser"],
    languages=["Lithuanian", "English"],
    max_budget=600,
    preferred_neighborhoods=["Antakalnis", "Užupis"],
)

all_roommies = [egle, matas, lukas, ieva, domas, austeja]
