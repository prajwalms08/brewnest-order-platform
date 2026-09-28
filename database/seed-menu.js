const database = db.getSiblingDB("brewnest");

if (database.menu.countDocuments() === 0) {
    database.menu.insertMany([
        {
            name: "Cappuccino",
            price: 120,
            category: "Coffee",
            modifiers: [
                {
                    name: "Extra Shot",
                    price: 30
                },
                {
                    name: "Oat Milk",
                    price: 20
                },
                {
                    name: "Extra Sugar",
                    price: 0
                }
            ]
        },
        {
            name: "Latte",
            price: 140,
            category: "Coffee",
            modifiers: [
                {
                    name: "Extra Shot",
                    price: 30
                },
                {
                    name: "Oat Milk",
                    price: 20
                },
                {
                    name: "Vanilla",
                    price: 20
                }
            ]
        },
        {
            name: "Espresso",
            price: 100,
            category: "Coffee",
            modifiers: [
                {
                    name: "Extra Shot",
                    price: 30
                },
                {
                    name: "Extra Sugar",
                    price: 0
                }
            ]
        },
        {
            name: "Cold Coffee",
            price: 160,
            category: "Beverages",
            modifiers: [
                {
                    name: "Extra Ice Cream",
                    price: 30
                },
                {
                    name: "Vanilla",
                    price: 20
                },
                {
                    name: "Chocolate",
                    price: 20
                }
            ]
        },
        {
            name: "Chocolate Cake",
            price: 180,
            category: "Desserts",
            modifiers: [
                {
                    name: "Extra Chocolate",
                    price: 25
                },
                {
                    name: "Ice Cream",
                    price: 30
                }
            ]
        }
    ]);

    print("BrewNest menu seeded successfully");
} else {
    print("BrewNest menu already exists");
}