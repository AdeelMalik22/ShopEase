"""
Management command to populate the database with sample data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.products.models import Category, Product
import os


class Command(BaseCommand):
    help = 'Populate database with sample users, categories, and products'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...\n')

        # Create users
        self.create_users()

        # Create categories
        categories = self.create_categories()

        # Create products
        self.create_products(categories)

        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))

    def create_users(self):
        """Create sample users"""
        self.stdout.write('Creating users...')

        users_data = [
            {
                'username': 'admin',
                'email': 'admin@shopease.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'username': 'john_doe',
                'email': 'john.doe@example.com',
                'password': 'user123',
                'first_name': 'John',
                'last_name': 'Doe',
                'is_superuser': False,
                'is_staff': False,
                'profile': {
                    'phone': '555-123-4567',
                    'address_line1': '123 Main Street',
                    'city': 'New York',
                    'state': 'NY',
                    'postal_code': '10001',
                    'country': 'United States',
                }
            },
            {
                'username': 'jane_smith',
                'email': 'jane.smith@example.com',
                'password': 'user123',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'is_superuser': False,
                'is_staff': False,
                'profile': {
                    'phone': '555-234-5678',
                    'address_line1': '456 Oak Avenue',
                    'city': 'Los Angeles',
                    'state': 'CA',
                    'postal_code': '90001',
                    'country': 'United States',
                }
            },
            {
                'username': 'bob_wilson',
                'email': 'bob.wilson@example.com',
                'password': 'user123',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'is_superuser': False,
                'is_staff': False,
                'profile': {
                    'phone': '555-345-6789',
                    'address_line1': '789 Pine Road',
                    'city': 'Chicago',
                    'state': 'IL',
                    'postal_code': '60601',
                    'country': 'United States',
                }
            },
            {
                'username': 'alice_johnson',
                'email': 'alice.johnson@example.com',
                'password': 'user123',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'is_superuser': False,
                'is_staff': False,
                'profile': {
                    'phone': '555-456-7890',
                    'address_line1': '321 Elm Street',
                    'city': 'Houston',
                    'state': 'TX',
                    'postal_code': '77001',
                    'country': 'United States',
                }
            },
        ]

        for user_data in users_data:
            profile_data = user_data.pop('profile', None)
            username = user_data['username']

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_superuser': user_data['is_superuser'],
                    'is_staff': user_data['is_staff'],
                }
            )

            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f'  Created user: {username}')

                # Update profile if profile data provided
                if profile_data and hasattr(user, 'profile'):
                    for key, value in profile_data.items():
                        setattr(user.profile, key, value)
                    user.profile.save()
            else:
                self.stdout.write(f'  User exists: {username}')

    def create_categories(self):
        """Create sample categories"""
        self.stdout.write('\nCreating categories...')

        categories_data = [
            {
                'name': 'Electronics',
                'slug': 'electronics',
                'description': 'Latest electronic gadgets, devices, and accessories. From smartphones to smart home devices.',
            },
            {
                'name': 'Clothing',
                'slug': 'clothing',
                'description': 'Fashion and apparel for men, women, and children. Stay stylish with our latest collection.',
            },
            {
                'name': 'Home & Garden',
                'slug': 'home-garden',
                'description': 'Everything for your home and garden. Furniture, decor, and gardening supplies.',
            },
            {
                'name': 'Sports & Outdoors',
                'slug': 'sports-outdoors',
                'description': 'Sports equipment, outdoor gear, and fitness accessories for an active lifestyle.',
            },
            {
                'name': 'Books & Media',
                'slug': 'books-media',
                'description': 'Books, music, movies, and educational materials for learning and entertainment.',
            },
            {
                'name': 'Beauty & Health',
                'slug': 'beauty-health',
                'description': 'Skincare, cosmetics, and health products for your wellbeing.',
            },
            {
                'name': 'Toys & Games',
                'slug': 'toys-games',
                'description': 'Toys, games, and puzzles for kids and adults. Fun for the whole family.',
            },
            {
                'name': 'Automotive',
                'slug': 'automotive',
                'description': 'Car accessories, parts, and tools for automotive enthusiasts.',
            },
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'is_active': True,
                }
            )
            categories[cat_data['slug']] = cat
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {cat_data["name"]}')

        return categories

    def create_products(self, categories):
        """Create sample products"""
        self.stdout.write('\nCreating products...')

        products_data = [
            # Electronics
            {
                'category': 'electronics',
                'name': 'Wireless Bluetooth Headphones',
                'slug': 'wireless-bluetooth-headphones',
                'description': 'Premium wireless headphones with active noise cancellation, 30-hour battery life, and crystal-clear audio. Perfect for music lovers and professionals.',
                'price': 79.99,
                'compare_price': 99.99,
                'stock': 50,
                'image': 'products/headphones.jpg',
                'is_featured': True,
            },
            {
                'category': 'electronics',
                'name': 'Smart Watch Pro',
                'slug': 'smart-watch-pro',
                'description': 'Advanced smartwatch with fitness tracking, heart rate monitor, GPS, and 7-day battery life. Stay connected and healthy.',
                'price': 199.99,
                'compare_price': 249.99,
                'stock': 30,
                'image': 'products/smartwatch.jpg',
                'is_featured': True,
            },
            {
                'category': 'electronics',
                'name': 'Portable Power Bank 20000mAh',
                'slug': 'portable-power-bank',
                'description': 'High-capacity portable charger with fast charging support. Charge multiple devices simultaneously.',
                'price': 39.99,
                'compare_price': None,
                'stock': 100,
                'image': 'products/powerbank.jpg',
                'is_featured': False,
            },
            {
                'category': 'electronics',
                'name': 'USB-C Hub Adapter 7-in-1',
                'slug': 'usb-c-hub-adapter',
                'description': 'Multi-port USB-C hub with HDMI, USB 3.0, SD card reader, and PD charging. Essential for professionals.',
                'price': 49.99,
                'compare_price': 59.99,
                'stock': 75,
                'image': 'products/usbhub.jpg',
                'is_featured': False,
            },
            {
                'category': 'electronics',
                'name': 'Ultra-Slim Laptop 15.6"',
                'slug': 'ultra-slim-laptop',
                'description': 'Powerful and lightweight laptop with Intel i7 processor, 16GB RAM, and 512GB SSD. Perfect for work and play.',
                'price': 899.99,
                'compare_price': 1099.99,
                'stock': 15,
                'image': 'products/laptop.jpg',
                'is_featured': True,
            },
            {
                'category': 'electronics',
                'name': 'Digital Tablet 10.5"',
                'slug': 'digital-tablet',
                'description': 'Versatile tablet with stunning display, stylus support, and all-day battery. Great for creativity and productivity.',
                'price': 449.99,
                'compare_price': 499.99,
                'stock': 25,
                'image': 'products/tablet.jpg',
                'is_featured': False,
            },

            # Clothing
            {
                'category': 'clothing',
                'name': 'Classic Cotton T-Shirt',
                'slug': 'classic-cotton-tshirt',
                'description': 'Premium 100% cotton t-shirt with a comfortable fit. Available in multiple colors. Machine washable.',
                'price': 24.99,
                'compare_price': 29.99,
                'stock': 200,
                'image': 'products/tshirt.jpg',
                'is_featured': True,
            },
            {
                'category': 'clothing',
                'name': 'Slim Fit Denim Jeans',
                'slug': 'slim-fit-denim-jeans',
                'description': 'Classic slim-fit denim jeans with stretch comfort. Durable and stylish for everyday wear.',
                'price': 59.99,
                'compare_price': 79.99,
                'stock': 150,
                'image': 'products/jeans.jpg',
                'is_featured': True,
            },
            {
                'category': 'clothing',
                'name': 'Running Sneakers Pro',
                'slug': 'running-sneakers-pro',
                'description': 'Lightweight running shoes with advanced cushioning and breathable mesh. Perfect for athletes.',
                'price': 89.99,
                'compare_price': 119.99,
                'stock': 80,
                'image': 'products/sneakers.jpg',
                'is_featured': False,
            },
            {
                'category': 'clothing',
                'name': 'Winter Parka Jacket',
                'slug': 'winter-parka-jacket',
                'description': 'Warm and waterproof winter jacket with hood. Features multiple pockets and insulated lining.',
                'price': 129.99,
                'compare_price': 159.99,
                'stock': 40,
                'image': 'products/jacket.jpg',
                'is_featured': False,
            },
            {
                'category': 'clothing',
                'name': 'Summer Floral Dress',
                'slug': 'summer-floral-dress',
                'description': 'Beautiful floral print dress perfect for summer. Lightweight and comfortable fabric.',
                'price': 49.99,
                'compare_price': 64.99,
                'stock': 60,
                'image': 'products/dress.jpg',
                'is_featured': True,
            },
            {
                'category': 'clothing',
                'name': 'Cozy Knit Sweater',
                'slug': 'cozy-knit-sweater',
                'description': 'Soft and warm knit sweater for cool weather. Classic design that never goes out of style.',
                'price': 54.99,
                'compare_price': 69.99,
                'stock': 70,
                'image': 'products/sweater.jpg',
                'is_featured': False,
            },

            # Home & Garden
            {
                'category': 'home-garden',
                'name': 'Modern Table Lamp',
                'slug': 'modern-table-lamp',
                'description': 'Stylish table lamp with adjustable brightness. Perfect for bedside or office desk.',
                'price': 45.99,
                'compare_price': 55.99,
                'stock': 45,
                'image': 'products/lamp.jpg',
                'is_featured': True,
            },
            {
                'category': 'home-garden',
                'name': 'Decorative Throw Cushion',
                'slug': 'decorative-throw-cushion',
                'description': 'Soft and comfortable decorative cushion. Adds a pop of color to any room.',
                'price': 19.99,
                'compare_price': 24.99,
                'stock': 100,
                'image': 'products/cushion.jpg',
                'is_featured': False,
            },
            {
                'category': 'home-garden',
                'name': 'Ceramic Flower Vase',
                'slug': 'ceramic-flower-vase',
                'description': 'Elegant ceramic vase for fresh or dried flowers. Beautiful centerpiece for any table.',
                'price': 34.99,
                'compare_price': None,
                'stock': 55,
                'image': 'products/vase.jpg',
                'is_featured': False,
            },

            # Sports & Outdoors
            {
                'category': 'sports-outdoors',
                'name': 'Premium Yoga Mat',
                'slug': 'premium-yoga-mat',
                'description': 'Non-slip yoga mat with extra cushioning. Perfect for yoga, pilates, and floor exercises.',
                'price': 29.99,
                'compare_price': 39.99,
                'stock': 80,
                'image': 'products/yoga_mat.jpg',
                'is_featured': True,
            },
            {
                'category': 'sports-outdoors',
                'name': 'Adjustable Dumbbell Set',
                'slug': 'adjustable-dumbbell-set',
                'description': 'Space-saving adjustable dumbbells from 5-50 lbs. Perfect for home workouts.',
                'price': 199.99,
                'compare_price': 249.99,
                'stock': 25,
                'image': 'products/dumbbell.jpg',
                'is_featured': True,
            },
            {
                'category': 'sports-outdoors',
                'name': 'Mountain Bike 26"',
                'slug': 'mountain-bike-26',
                'description': 'Durable mountain bike with 21-speed gears and disc brakes. Ready for any terrain.',
                'price': 349.99,
                'compare_price': 449.99,
                'stock': 10,
                'image': 'products/bike.jpg',
                'is_featured': False,
            },

            # Books & Media
            {
                'category': 'books-media',
                'name': 'The Art of Programming',
                'slug': 'art-of-programming',
                'description': 'Comprehensive guide to software development best practices. Essential for developers.',
                'price': 39.99,
                'compare_price': 49.99,
                'stock': 50,
                'image': 'products/book1.jpg',
                'is_featured': True,
            },
            {
                'category': 'books-media',
                'name': 'Mindfulness for Beginners',
                'slug': 'mindfulness-beginners',
                'description': 'Learn the basics of mindfulness and meditation. Start your journey to inner peace.',
                'price': 14.99,
                'compare_price': 19.99,
                'stock': 75,
                'image': 'products/book2.jpg',
                'is_featured': False,
            },

            # Beauty & Health
            {
                'category': 'beauty-health',
                'name': 'Hydrating Skincare Set',
                'slug': 'hydrating-skincare-set',
                'description': 'Complete skincare routine with cleanser, toner, and moisturizer. For all skin types.',
                'price': 59.99,
                'compare_price': 79.99,
                'stock': 40,
                'image': 'products/skincare.jpg',
                'is_featured': True,
            },
            {
                'category': 'beauty-health',
                'name': 'Luxury Perfume 100ml',
                'slug': 'luxury-perfume',
                'description': 'Elegant fragrance with notes of jasmine, sandalwood, and vanilla. Long-lasting scent.',
                'price': 89.99,
                'compare_price': 119.99,
                'stock': 30,
                'image': 'products/perfume.jpg',
                'is_featured': False,
            },

            # Toys & Games
            {
                'category': 'toys-games',
                'name': 'Building Blocks Set 500pcs',
                'slug': 'building-blocks-set',
                'description': 'Creative building blocks for endless possibilities. Develops creativity and motor skills.',
                'price': 34.99,
                'compare_price': 44.99,
                'stock': 60,
                'image': 'products/toy1.jpg',
                'is_featured': True,
            },
            {
                'category': 'toys-games',
                'name': 'Strategy Board Game',
                'slug': 'strategy-board-game',
                'description': 'Engaging strategy game for 2-6 players. Hours of fun for family game nights.',
                'price': 29.99,
                'compare_price': None,
                'stock': 45,
                'image': 'products/toy2.jpg',
                'is_featured': False,
            },

            # Automotive
            {
                'category': 'automotive',
                'name': 'Fast Car Charger Dual USB',
                'slug': 'fast-car-charger',
                'description': 'Quick charge car adapter with dual USB ports. Compatible with all smartphones.',
                'price': 19.99,
                'compare_price': 24.99,
                'stock': 100,
                'image': 'products/carcharger.jpg',
                'is_featured': False,
            },
            {
                'category': 'automotive',
                'name': 'Magnetic Phone Mount',
                'slug': 'magnetic-phone-mount',
                'description': 'Strong magnetic car phone holder with 360° rotation. Easy one-hand operation.',
                'price': 24.99,
                'compare_price': 29.99,
                'stock': 85,
                'image': 'products/carmount.jpg',
                'is_featured': True,
            },
        ]

        for prod_data in products_data:
            category = categories.get(prod_data['category'])
            if not category:
                self.stdout.write(self.style.WARNING(f'  Category not found: {prod_data["category"]}'))
                continue

            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={
                    'category': category,
                    'name': prod_data['name'],
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'compare_price': prod_data['compare_price'],
                    'stock': prod_data['stock'],
                    'image': prod_data.get('image', ''),
                    'is_active': True,
                    'is_featured': prod_data['is_featured'],
                }
            )

            # Update image if product exists but doesn't have image
            if not created and not product.image and prod_data.get('image'):
                product.image = prod_data['image']
                product.save()

            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {prod_data["name"]}')

