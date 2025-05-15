from app import app, db, Category, Product, User
from werkzeug.security import generate_password_hash

try:
    with app.app_context():
        # Drop and recreate tables to ensure a clean state
        db.drop_all()
        db.create_all()

        # Create admin user with explicit hashing method
        admin_password = generate_password_hash('admin123', method='pbkdf2:sha256')
        print(f"Generated admin password hash: {admin_password}")
        admin = User(username='admin', password=admin_password)
        db.session.add(admin)

        # Create categories with slugs and descriptions
        categories = [
            Category(
                name='Cereal Seeds',
                slug='cereal-seeds',
                description='Discover our Cereal Seeds, designed for high yields and resilience, updated as of 01:23 PM CEST, May 15, 2025.'
            ),
            Category(
                name='Vegetable Seeds',
                slug='vegetable-seeds',
                description='Explore our Vegetable Seeds, optimized for organic farming and flavor, refreshed on 01:23 PM CEST, May 15, 2025.'
            ),
            Category(
                name='Medicinal Seeds',
                slug='medicinal-seeds',
                description='Learn about our Medicinal Seeds, crafted for herbal remedies, enhanced on 01:23 PM CEST, May 15, 2025.'
            ),
        ]
        db.session.add_all(categories)
        db.session.commit()

        # Create seed products with dummy image paths and prices
        products = [
            Product(
                name='High-Yield Wheat Seed',
                description='A genetically optimized wheat seed designed for high yield and drought resistance, ideal for sustainable agriculture in arid regions.',
                category_id=1,
                image_filename='https://dummyimage.com/640x480/2563eb/ffffff&text=Wheat+Seed',
                price=50.00,
                discounted_price=45.00  # Discounted
            ),
            Product(
                name='Durum Barley Seed',
                description='Robust barley seeds engineered for enhanced grain quality and resistance to fungal pathogens, suitable for large-scale farming.',
                category_id=1,
                image_filename='https://dummyimage.com/640x480/2563eb/ffffff&text=Barley+Seed',
                price=45.00
            ),
            Product(
                name='Hybrid Tomato Seed',
                description='High-vigor tomato seeds with improved germination rates, bred for uniform fruit size and resistance to blight.',
                category_id=2,
                image_filename='https://dummyimage.com/640x480/2563eb/ffffff&text=Tomato+Seed',
                price=30.00,
                discounted_price=25.00  # Discounted
            ),
            Product(
                name='Organic Spinach Seed',
                description='Non-GMO spinach seeds optimized for rapid growth and high nutrient content, perfect for organic farming.',
                category_id=2,
                image_filename='https://dummyimage.com/640x480/2563eb/ffffff&text=Spinach+Seed',
                price=25.00
            ),
            Product(
                name='Chamomile Seed',
                description='Medicinal chamomile seeds for cultivation of plants used in herbal remedies, with enhanced essential oil content.',
                category_id=3,
                image_filename='https://dummyimage.com/640x480/2563eb/ffffff&text=Chamomile+Seed',
                price=20.00,
                discounted_price=18.00  # Discounted
            ),
            Product(
                name='Milk Thistle Seed',
                description='Seeds for growing milk thistle, known for its liver-supporting properties, optimized for high silymarin content.',
                category_id=3,
                image_filename='https://dummyimage.com/640x480/2563eb/ffffff&text=Milk+Thistle+Seed',
                price=22.00
            ),
        ]
        db.session.add_all(products)
        db.session.commit()

        print("Database seeded successfully!")
except Exception as e:
    print(f"Error during seeding: {e}")