def main(fn_call):
    function_name = fn_call["value"]["name"]
    args = fn_call["value"]["arguments"]
    
    if function_name == "get_top_products":
        return get_top_products(args)
    elif function_name == "get_product_details":
        return get_product_details(args)
    else:
        raise Exception("Invalid function error")
    
def get_top_products(args):
    return [
        "Blueridge BMY922C",
        "Blueridge BMM1822-6W-6W",
        "Blueridge BMKH1824/O"
    ]

def get_product_details(args):
    product_name = args.product_name  
    return {
        "Blueridge BMY922C": {
            "price": "$439.00",
            "num_reviews": 625,
            "avg_rating": 5,
            "reviews": [
                {
                    "title": "Super quiet unit - inside and out!",
                    "desc": "I've agonized over putting a mini-split in for a long time, as I heat and cool my office above the garage separately, turning off the house most of the day. Let me tell you - this unit is DEAD QUIET inside and out - no compressor noise outside, just a gentle hum of the fan."
                },
                {
                    "title": "Not too bad for the price",
                    "desc": "Over all the product is not too bad. I do not think the average homeowner can install these by themselves. I found the instructions very vague and incomplete. After reading them I simply threw them away and installed as I have other units of the same type. I think they will suffice for what I needed"
                }
            ]
        },
        "Blueridge BMM1822-6W-6W": {
            "price": "$1989.00",
            "num_reviews": 303,
            "avg_rating": 4.9,
            "reviews": [
                {
                    "title": "Great Unit - Not without its quirks.",
                    "desc": "I waited to provide my comments as I wanted to use the product for several months prior to review. I'm happy to say that I still provided a 5-star review. I purchased a 4 unit system, 2 wall mounts and 2 ceiling mounts. I live in NH and have been using the system exclusively for heat since I got it"
                },
                {
                    "title": "Very efficient and good company to work with. Only one issu",
                    "desc": "It cools our rooms effortlessly and keeps the temperature at a constant level. They are quiet with unfortunately the one unit over our bed. It creaks, and I was advised it was probably due to the contraction and expansion of the materials. There only solution was to loosen some screws, but it is ..."
                }
            ]
        },
        "Blueridge BMKH1824/O": {
            "price": "$949.00",
            "num_reviews": 110,
            "avg_rating": 4.5, # it's actually 4.9 but using 4.5 for variation
            "reviews": [
                {
                    "title": "Running great",
                    "desc": "Finally finished the install, the ceiling fan makes more noise than the Blueridge cooling unit, really quiet and seems to cool out Master bedroom easily. My wife is very happy."
                },
                {
                    "title": "Quiet, efficient, and literally took control of our cooling.",
                    "desc": "Install this 12,000btu unit with a 30.5 SEER rating with a bit of skepticism. All that was put to rest as the unit has basically taken control of cooling our 1200 sq ft house and our main unit only come on for about 5-6 hours a day even on the hottest and my muggiest days over 100 this summer. Keeps our house cool at 73-74 degrees all day long and is extremely quiet. Easy to install. I am a DIYer and had it done in 6.5 hours and had to go through a brick wall to exit the lines from the house. Easily done in a day with a helper. All in all, very pleased with the unit and how it has performed."
                }
            ]
        }
    }[product_name]

