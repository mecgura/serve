"""
MecGuraServe - Setup All Services
Run: py manage.py setup_services
"""

from django.core.management.base import BaseCommand
from services.models import ServiceCategory, Service


class Command(BaseCommand):
    help = 'Setup all services for MecGuraServe'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up services...'))
        
        # Create Categories
        categories = {
            'ordering': ServiceCategory.objects.create(
                name='Smart Ordering', icon='fas fa-mobile-alt',
                description='Advanced ordering features', order=1
            ),
            'ai': ServiceCategory.objects.create(
                name='AI Features', icon='fas fa-brain',
                description='AI-powered automation', order=2
            ),
            'payment': ServiceCategory.objects.create(
                name='Payment & Billing', icon='fas fa-credit-card',
                description='Payment and billing features', order=3
            ),
            'guest': ServiceCategory.objects.create(
                name='Guest Experience', icon='fas fa-concierge-bell',
                description='Enhanced guest experience', order=4
            ),
            'operations': ServiceCategory.objects.create(
                name='Operations', icon='fas fa-cogs',
                description='Operational efficiency', order=5
            ),
            'marketing': ServiceCategory.objects.create(
                name='Marketing & Loyalty', icon='fas fa-bullhorn',
                description='Marketing and customer retention', order=6
            ),
            'sustainability': ServiceCategory.objects.create(
                name='Sustainability', icon='fas fa-leaf',
                description='Eco-friendly features', order=7
            ),
            'security': ServiceCategory.objects.create(
                name='Security & Access', icon='fas fa-shield-alt',
                description='Security features', order=8
            ),
        }
        
        # Create Services
        services = [
            # ===== SMART ORDERING =====
            {
                'category': 'ordering',
                'name': 'AI Voice Ordering',
                'slug': 'ai-voice-ordering',
                'short_description': 'Customers can order via phone call in Hindi/English/Punjabi',
                'full_description': 'AI-powered phone system that takes orders automatically. Customers call, speak naturally, and AI understands and places the order directly in kitchen.',
                'icon': 'fas fa-microphone',
                'price_type': 'monthly',
                'price': 999,
                'original_price': 1999,
                'features': ['Multi-language support (Hindi, English, Punjabi, Tamil)', '24/7 availability', 'Direct kitchen integration', 'Order confirmation SMS', 'Missed call callback'],
                'manual_title': 'How to Setup AI Voice Ordering',
                'manual_content': '''1. Go to Services → AI Voice Ordering → Settings
2. Add your restaurant phone number
3. Select supported languages
4. Test with a sample call
5. Share the AI number with customers

Usage:
- Customer calls the AI number
- AI greets and asks for order
- Customer speaks order naturally
- AI confirms and sends to kitchen
- SMS confirmation sent to customer

Tips:
- Test daily with sample orders
- Update menu items regularly
- Check call logs for missed orders''',
            },
            {
                'category': 'ordering',
                'name': 'AR Menu (Augmented Reality)',
                'slug': 'ar-menu',
                'short_description': 'Customers see 3D food items before ordering',
                'full_description': 'AR-powered menu that shows realistic 3D food models. Customers scan QR code and see dishes in actual size before ordering. Increases order value by 20-26%.',
                'icon': 'fas fa-vr-cardboard',
                'price_type': 'monthly',
                'price': 1499,
                'original_price': 2999,
                'features': ['3D dish visualization', '20-26% higher order value', 'No app download needed', 'Allergen info display', 'Social media share'],
                'manual_title': 'How to Setup AR Menu',
                'manual_content': '''1. Go to Services → AR Menu → Settings
2. Upload dish photos (multiple angles)
3. AI generates 3D models automatically
4. Preview and adjust if needed
5. QR codes auto-generated for tables

Usage:
- Customer scans table QR code
- AR menu opens in browser
- Tap any dish to see 3D view
- Rotate, zoom, view from angles
- Add to cart directly from AR

Tips:
- Upload high-quality photos
- Update seasonal dishes
- Promote AR feature on table tents''',
            },
            {
                'category': 'ordering',
                'name': 'Smart Table Recommendation',
                'slug': 'smart-table-recommend',
                'short_description': 'AI suggests best table based on guest type',
                'full_description': 'AI analyzes guest type (couple, family, business) and suggests the perfect table. Improves guest satisfaction and table utilization.',
                'icon': 'fas fa-chair',
                'price_type': 'monthly',
                'price': 499,
                'original_price': 999,
                'features': ['Guest type detection', 'Automatic table suggestion', 'VIP table management', 'Occupancy optimization', 'Guest preference memory'],
                'manual_title': 'How to Setup Smart Table Recommendation',
                'manual_content': '''1. Go to Services → Smart Table → Settings
2. Tag tables with attributes (romantic, family, business, VIP)
3. Enable auto-suggestion
4. Train staff on recommendation flow

Usage:
- Customer arrives/walks in
- System asks: "How many guests? Any occasion?"
- AI suggests best table
- Staff guides to recommended table

Tips:
- Keep table tags updated
- Review suggestion accuracy weekly''',
            },
            {
                'category': 'ordering',
                'name': 'Digital Key (Room Unlock)',
                'slug': 'digital-key',
                'short_description': 'Guests unlock rooms with smartphone',
                'full_description': 'NFC/Bluetooth based digital room keys. Guests use phone to unlock rooms, no physical key needed.',
                'icon': 'fas fa-key',
                'price_type': 'monthly',
                'price': 799,
                'original_price': 1499,
                'features': ['Phone as room key', 'Check-in to unlock', 'Share access with family', 'Auto-expire on checkout', 'Access history log'],
                'manual_title': 'How to Setup Digital Key',
                'manual_content': '''1. Install smart locks on rooms
2. Configure in Services → Digital Key → Settings
3. Map room numbers to lock IDs
4. Test with sample unlock

Usage:
- Guest checks in online
- Digital key activates automatically
- Guest taps phone on lock
- Room unlocks instantly

Requirements:
- Smart locks (NFC/Bluetooth compatible)
- WiFi in all rooms''',
            },
            {
                'category': 'ordering',
                'name': 'Contactless Payment',
                'slug': 'contactless-payment',
                'short_description': 'UPI, cards, wallet - scan and pay',
                'full_description': 'Multiple contactless payment options - UPI QR, card tap, wallet. Fast checkout without waiting for bill.',
                'icon': 'fas fa-qrcode',
                'price_type': 'free',
                'price': 0,
                'features': ['UPI QR payment', 'Card tap payment', 'Wallet integration', 'Auto receipt', 'Split bill option'],
                'manual_title': 'How to Setup Contactless Payment',
                'manual_content': '''1. Go to Settings → Payment Methods
2. Add UPI ID (Google Pay, PhonePe, etc.)
3. Enable card payments (requires POS)
4. Test with sample transaction

Usage:
- Customer finishes meal
- Bill appears on phone
- Tap "Pay Now"
- Scan QR or tap card
- Payment confirmed instantly''',
            },
            
            # ===== AI FEATURES =====
            {
                'category': 'ai',
                'name': 'AI Menu Engineering',
                'slug': 'ai-menu-engineering',
                'short_description': 'AI optimizes menu for maximum profit',
                'full_description': 'AI analyzes sales data, food costs, and customer behavior to optimize menu. Suggests which items to promote, price, or remove.',
                'icon': 'fas fa-chart-line',
                'price_type': 'monthly',
                'price': 999,
                'original_price': 1999,
                'features': ['Profit margin analysis', 'Dead item detection', 'Price optimization', 'Seasonal suggestions', 'Competitor analysis'],
                'manual_title': 'How to Use AI Menu Engineering',
                'manual_content': '''1. Go to Services → AI Menu Engineering
2. View dashboard with insights
3. Follow AI suggestions

Dashboard Shows:
- Top 5 profitable items
- Bottom 5 items (consider removing)
- Price increase suggestions
- Seasonal item recommendations

Usage:
- Review daily for first week
- Implement 1-2 suggestions per week
- Track revenue changes monthly''',
            },
            {
                'category': 'ai',
                'name': 'Predictive Inventory',
                'slug': 'predictive-inventory',
                'short_description': 'AI predicts demand, reduces food waste',
                'full_description': 'AI predicts how much of each ingredient to buy based on weather, festivals, past orders. Reduces food waste by 30%.',
                'icon': 'fas fa-boxes',
                'price_type': 'monthly',
                'price': 1499,
                'original_price': 2999,
                'features': ['Demand forecasting', 'Auto purchase orders', 'Waste reduction alerts', 'Festival/event integration', 'Supplier management'],
                'manual_title': 'How to Setup Predictive Inventory',
                'manual_content': '''1. Go to Services → Predictive Inventory
2. Add ingredients with current stock
3. Set minimum stock levels
4. Connect suppliers (optional)

Daily Usage:
- Check morning prediction report
- Review suggested purchase orders
- Approve/modify before 10 AM
- System auto-tracks usage

Weekly:
- Review waste report
- Adjust predictions if needed''',
            },
            {
                'category': 'ai',
                'name': 'AI Revenue Optimizer',
                'slug': 'ai-revenue-optimizer',
                'short_description': 'Dynamic pricing based on demand',
                'full_description': 'AI adjusts prices in real-time based on demand, time, weather, events. Maximizes revenue while staying competitive.',
                'icon': 'fas fa-dollar-sign',
                'price_type': 'monthly',
                'price': 1999,
                'original_price': 3999,
                'features': ['Dynamic pricing', 'Time-based pricing', 'Weather-based pricing', 'Event-based pricing', 'Revenue dashboard'],
                'manual_title': 'How to Use AI Revenue Optimizer',
                'manual_content': '''1. Go to Services → Revenue Optimizer
2. Set base prices for all items
3. Configure pricing rules:
   - Peak hours: +10%
   - Off-peak: -10%
   - Rainy day: -15%
   - Festival: +20%

Monitoring:
- Check daily revenue vs yesterday
- Review pricing changes log
- Adjust rules as needed''',
            },
            {
                'category': 'ai',
                'name': 'AI Concierge',
                'slug': 'ai-concierge',
                'short_description': 'WhatsApp AI assistant for guests',
                'full_description': 'AI chatbot on WhatsApp that handles guest requests 24/7. Room service, spa booking, recommendations - all automated.',
                'icon': 'fas fa-robot',
                'price_type': 'monthly',
                'price': 1499,
                'original_price': 2999,
                'features': ['24/7 WhatsApp support', 'Service booking', 'Recommendations', 'FAQ handling', 'Human handoff'],
                'manual_title': 'How to Setup AI Concierge',
                'manual_content': '''1. Connect WhatsApp Business API
2. Go to Services → AI Concierge → Settings
3. Train AI on your menu/services
4. Set business hours
5. Test with sample conversations

Usage:
- Guest sends WhatsApp message
- AI responds instantly
- Handles: menu, booking, info
- Complex queries → human staff

Tips:
- Update AI knowledge weekly
- Review conversation logs daily''',
            },
            {
                'category': 'ai',
                'name': 'AI Guest Analytics',
                'slug': 'ai-guest-analytics',
                'short_description': 'Understand guest behavior and preferences',
                'full_description': 'AI tracks guest visits, orders, preferences. Creates profiles for personalized service. Predicts return visits.',
                'icon': 'fas fa-users',
                'price_type': 'monthly',
                'price': 999,
                'original_price': 1999,
                'features': ['Guest profiles', 'Visit tracking', 'Order history', 'Preference analysis', 'Loyalty scoring'],
                'manual_title': 'How to Use AI Guest Analytics',
                'manual_content': '''1. Go to Services → Guest Analytics
2. View guest dashboard
3. See top guests, their preferences

Dashboard Shows:
- Total unique guests
- Return guest percentage
- Average spend per guest
- Popular items by guest type

Usage:
- Identify VIP guests
- Create personalized offers
- Welcome returning guests''',
            },
            
            # ===== PAYMENT & BILLING =====
            {
                'category': 'payment',
                'name': 'Advance Payment',
                'slug': 'advance-payment',
                'short_description': 'Collect advance for reservations',
                'full_description': 'Collect advance payment for table reservations. Reduces no-shows by 60%.',
                'icon': 'fas fa-hand-holding-usd',
                'price_type': 'monthly',
                'price': 499,
                'original_price': 999,
                'features': ['Online advance collection', 'Auto refund on cancel', 'No-show protection', 'Reservation management', 'Payment tracking'],
                'manual_title': 'How to Setup Advance Payment',
                'manual_content': '''1. Go to Settings → Payments → Advance
2. Set advance amount (e.g., ₹100)
3. Configure refund policy
4. Connect Razorpay

Usage:
- Customer books table online
- Advance payment required
- Razorpay processes payment
- Confirmation sent via WhatsApp
- Advance adjusted on final bill''',
            },
            {
                'category': 'payment',
                'name': 'Payment Reminders',
                'slug': 'payment-reminders',
                'short_description': 'Auto reminders for pending payments',
                'full_description': 'Automatic WhatsApp/SMS reminders for pending payments. Individual or bulk reminders.',
                'icon': 'fas fa-bell',
                'price_type': 'monthly',
                'price': 299,
                'original_price': 599,
                'features': ['Auto reminders', 'Bulk reminders', 'WhatsApp integration', 'Payment tracking', 'Escalation rules'],
                'manual_title': 'How to Setup Payment Reminders',
                'manual_content': '''1. Go to Services → Payment Reminders
2. Set reminder schedule:
   - 1 day after: Gentle reminder
   - 3 days: Firm reminder
   - 7 days: Final notice
3. Enable WhatsApp/SMS

Usage:
- System auto-sends reminders
- Track in dashboard
- Override if needed''',
            },
            {
                'category': 'payment',
                'name': 'Digital Tipping',
                'slug': 'digital-tipping',
                'short_description': 'QR code tips directly to staff accounts',
                'full_description': 'QR code on bill for tipping. Money goes directly to staff bank accounts. Increases tips by 50%.',
                'icon': 'fas fa-heart',
                'price_type': 'monthly',
                'price': 199,
                'original_price': 399,
                'features': ['QR code tipping', 'Direct staff payment', 'Tip tracking', 'Feedback with tip', 'Staff leaderboard'],
                'manual_title': 'How to Setup Digital Tipping',
                'manual_content': '''1. Go to Services → Digital Tipping
2. Add staff bank accounts/UPI IDs
3. Enable on bills
4. Set tip options (₹50, ₹100, Custom)

Usage:
- Bill includes tipping QR
- Customer scans and tips
- Money goes to staff directly
- Staff sees in their dashboard''',
            },
            
            # ===== GUEST EXPERIENCE =====
            {
                'category': 'guest',
                'name': 'AI Concierge (Guest Facing)',
                'slug': 'ai-concierge-guest',
                'short_description': 'Guests chat with AI for any request',
                'full_description': 'Guest-facing AI that handles all requests - room service, spa, recommendations. Available via WhatsApp, SMS, or in-app.',
                'icon': 'fas fa-concierge-bell',
                'price_type': 'monthly',
                'price': 1499,
                'original_price': 2999,
                'features': ['24/7 availability', 'Multi-channel', 'Service booking', 'Local recommendations', 'Multilingual'],
                'manual_title': 'How to Setup AI Concierge for Guests',
                'manual_content': '''1. Go to Services → AI Concierge
2. Connect WhatsApp Business API
3. Train AI on your services
4. Set response templates
5. Test with sample queries

Channels:
- WhatsApp (primary)
- SMS (fallback)
- In-app chat

Usage:
- Guest sends request
- AI handles or routes to staff
- Response within 30 seconds''',
            },
            {
                'category': 'guest',
                'name': 'Multi-Language Support',
                'slug': 'multi-language',
                'short_description': 'Menu and support in 50+ languages',
                'full_description': 'Automatic translation of menu, notifications, and AI support in 50+ languages. Perfect for international tourists.',
                'icon': 'fas fa-language',
                'price_type': 'monthly',
                'price': 799,
                'original_price': 1499,
                'features': ['50+ languages', 'Auto translation', 'AI support in local language', 'Menu translation', 'Notification translation'],
                'manual_title': 'How to Setup Multi-Language',
                'manual_content': '''1. Go to Services → Multi-Language
2. Select primary language
3. Enable auto-translation
4. Test with sample content

Supported Languages:
- Hindi, English, Punjabi, Tamil
- Japanese, Korean, Chinese
- Spanish, French, German
- 40+ more languages

Usage:
- Guest selects language
- Menu auto-translates
- AI responds in that language''',
            },
            {
                'category': 'guest',
                'name': 'Mobile Check-in',
                'slug': 'mobile-checkin',
                'short_description': 'Guests check-in via phone, no reception wait',
                'full_description': 'Guests complete check-in on phone before arrival. Room key activates automatically. Zero wait at reception.',
                'icon': 'fas fa-mobile-alt',
                'price_type': 'monthly',
                'price': 999,
                'original_price': 1999,
                'features': ['Pre-arrival check-in', 'Digital ID verification', 'Room selection', 'Auto key activation', 'Welcome message'],
                'manual_title': 'How to Setup Mobile Check-in',
                'manual_content': '''1. Go to Services → Mobile Check-in
2. Configure check-in form
3. Set room availability
4. Enable digital key integration

Usage:
- Guest books room
- Gets check-in link via WhatsApp
- Fills form, uploads ID
- Room key activates on arrival
- No reception visit needed''',
            },
            {
                'category': 'guest',
                'name': 'Smart Room Controls',
                'slug': 'smart-room',
                'short_description': 'Voice/phone control for AC, lights, blinds',
                'full_description': 'IoT-enabled room controls. Guests use voice or phone to control AC, lighting, entertainment, blinds.',
                'icon': 'fas fa-home',
                'price_type': 'monthly',
                'price': 1999,
                'original_price': 3999,
                'features': ['Voice control', 'Phone app control', 'Temperature memory', 'Lighting scenes', 'Energy optimization'],
                'manual_title': 'How to Setup Smart Room Controls',
                'manual_content': '''1. Install smart devices (AC, lights, blinds)
2. Go to Services → Smart Room
3. Pair devices with rooms
4. Configure scenes:
   - Welcome: Lights 50%, AC 24°C
   - Sleep: Lights off, AC 22°C
   - Wake up: Lights gradual, AC 25°C

Requirements:
- Smart switches/ACs
- WiFi in all rooms
- Hub device per floor''',
            },
            {
                'category': 'guest',
                'name': 'WiFi Feedback System',
                'slug': 'wifi-feedback',
                'short_description': 'Real-time feedback when guests connect to WiFi',
                'full_description': 'Survey popup when guest connects to WiFi. Captures real-time feedback. Issues resolved before checkout.',
                'icon': 'fas fa-wifi',
                'price_type': 'monthly',
                'price': 399,
                'original_price': 799,
                'features': ['WiFi login survey', 'Real-time alerts', 'Issue tracking', 'Satisfaction score', 'Manager notifications'],
                'manual_title': 'How to Setup WiFi Feedback',
                'manual_content': '''1. Go to Services → WiFi Feedback
2. Configure WiFi portal
3. Add survey questions:
   - "Rate your check-in experience"
   - "How is your room?"
   - "Any issues so far?"
4. Set alert rules:
   - 3 stars or below → instant alert

Usage:
- Guest connects to WiFi
- Survey popup appears
- 1-tap rating
- Low rating → manager alerted''',
            },
            {
                'category': 'guest',
                'name': 'Activity Recommendations',
                'slug': 'activity-recommend',
                'short_description': 'AI suggests activities based on guest location',
                'full_description': 'AI recommends spa, dining, activities based on where guest is in resort. Increases upsell by 30%.',
                'icon': 'fas fa-map-marked-alt',
                'price_type': 'monthly',
                'price': 599,
                'original_price': 1199,
                'features': ['Location-based suggestions', 'Time-based offers', 'Personalized recommendations', 'Push notifications', 'Upsell tracking'],
                'manual_title': 'How to Use Activity Recommendations',
                'manual_content': '''1. Go to Services → Activity Recommendations
2. Map resort areas (pool, spa, restaurant)
3. Set offers per area
4. Enable notifications

Usage:
- Guest near pool → "Poolside cocktails 20% off"
- Guest at spa → "Full body massage ₹500 off"
- Guest at restaurant → "Happy hour special"

Tips:
- Change offers daily
- Track conversion rates''',
            },
            
            # ===== OPERATIONS =====
            {
                'category': 'operations',
                'name': 'Kitchen Display System',
                'slug': 'kitchen-display',
                'short_description': 'Digital screen for kitchen orders',
                'full_description': 'Replace paper KOT with digital kitchen display. Real-time orders, sound alerts, status tracking.',
                'icon': 'fas fa-desktop',
                'price_type': 'monthly',
                'price': 599,
                'original_price': 1199,
                'features': ['Real-time orders', 'Sound alerts', 'Status updates', 'Priority marking', 'Time tracking'],
                'manual_title': 'How to Setup Kitchen Display',
                'manual_content': '''1. Go to Services → Kitchen Display
2. Connect tablet/monitor to kitchen
3. Open kitchen URL on device
4. Configure sound alerts
5. Set auto-refresh interval

Usage:
- Order placed → appears on screen
- Sound alert plays
- Kitchen marks "Preparing" → "Ready"
- Waiter notified when ready

Tips:
- Mount screen at eye level
- Test sound volume daily''',
            },
            {
                'category': 'operations',
                'name': 'Predictive Maintenance',
                'slug': 'predictive-maintenance',
                'short_description': 'AI detects equipment issues before breakdown',
                'full_description': 'IoT sensors monitor equipment health. AI predicts failures before they happen. Zero downtime.',
                'icon': 'fas fa-tools',
                'price_type': 'monthly',
                'price': 999,
                'original_price': 1999,
                'features': ['Equipment monitoring', 'Failure prediction', 'Auto alerts', 'Maintenance scheduling', 'Cost tracking'],
                'manual_title': 'How to Setup Predictive Maintenance',
                'manual_content': '''1. Go to Services → Predictive Maintenance
2. List critical equipment (AC, generators, etc.)
3. Set monitoring parameters
4. Configure alert rules

Monitoring:
- AC: Temperature, runtime, errors
- Generator: Fuel, runtime, output
- Freezer: Temperature, compressor

Usage:
- Dashboard shows equipment health
- Yellow alert: Check soon
- Red alert: Fix immediately''',
            },
            {
                'category': 'operations',
                'name': 'Smart Energy Management',
                'slug': 'smart-energy',
                'short_description': 'AI optimizes energy usage, cuts costs 30%',
                'full_description': 'AI controls AC, lights, equipment based on occupancy. Reduces energy bill by 30%.',
                'icon': 'fas fa-bolt',
                'price_type': 'monthly',
                'price': 1499,
                'original_price': 2999,
                'features': ['Occupancy-based control', 'Auto on/off', 'Energy tracking', 'Cost savings report', 'Carbon footprint'],
                'manual_title': 'How to Setup Smart Energy',
                'manual_content': '''1. Go to Services → Smart Energy
2. Connect smart switches/thermostats
3. Set occupancy rules:
   - Room empty → AC off, lights off
   - Room occupied → normal settings
4. Set schedules:
   - Lobby: 6 AM - 11 PM
   - Pool: 6 AM - 10 PM

Usage:
- System auto-manages energy
- Check savings dashboard
- Adjust rules as needed''',
            },
            {
                'category': 'operations',
                'name': 'Autonomous Cleaning Robots',
                'slug': 'cleaning-robots',
                'short_description': 'Robots for lobby and corridor cleaning',
                'full_description': 'Deploy cleaning robots for common areas. 3x faster than manual, 24/7 available.',
                'icon': 'fas fa-robot',
                'price_type': 'monthly',
                'price': 2999,
                'original_price': 5999,
                'features': ['Auto cleaning', 'Schedule management', 'Area mapping', 'Performance tracking', 'Maintenance alerts'],
                'manual_title': 'How to Deploy Cleaning Robots',
                'manual_content': '''1. Purchase/lease robot units
2. Go to Services → Cleaning Robots
3. Map cleaning areas
4. Set cleaning schedules:
   - Lobby: Every 2 hours
   - Corridors: 6 AM, 2 PM, 10 PM
5. Monitor in dashboard

Requirements:
- Flat floor surfaces
- WiFi coverage
- Charging stations''',
            },
            
            # ===== MARKETING =====
            {
                'category': 'marketing',
                'name': 'Loyalty Program',
                'slug': 'loyalty-program',
                'short_description': 'Points, rewards, VIP tiers',
                'full_description': 'Automatic loyalty points on every order. VIP tiers with exclusive benefits. Increases repeat visits by 40%.',
                'icon': 'fas fa-crown',
                'price_type': 'monthly',
                'price': 699,
                'original_price': 1399,
                'features': ['Points system', 'VIP tiers', 'Reward redemption', 'Member exclusive offers', 'Referral program'],
                'manual_title': 'How to Setup Loyalty Program',
                'manual_content': '''1. Go to Services → Loyalty Program
2. Set point rules:
   - ₹10 spent = 1 point
   - 100 points = ₹50 reward
3. Define VIP tiers:
   - Bronze: 0-500 points
   - Silver: 500-2000 points
   - Gold: 2000+ points
4. Enable auto-enrollment

Usage:
- Customer orders → points auto-added
- Points balance via WhatsApp
- Redeem on next visit''',
            },
            {
                'category': 'marketing',
                'name': 'Automated Marketing',
                'slug': 'automated-marketing',
                'short_description': 'Auto WhatsApp/SMS campaigns',
                'full_description': 'Automated birthday wishes, festival offers, re-engagement campaigns. Set once, runs forever.',
                'icon': 'fas fa-envelope-open-text',
                'price_type': 'monthly',
                'price': 999,
                'original_price': 1999,
                'features': ['Birthday automation', 'Festival campaigns', 'Re-engagement', 'WhatsApp broadcasts', 'Campaign analytics'],
                'manual_title': 'How to Setup Automated Marketing',
                'manual_content': '''1. Go to Services → Automated Marketing
2. Create campaigns:
   - Birthday: "Happy Birthday! 20% off today"
   - Festival: "Diwali Special - Order now"
   - Re-engage: "We miss you! Here's ₹100 off"
3. Set triggers:
   - Birthday: Auto on birthday
   - Festival: Auto on festival date
   - Re-engage: After 30 days no visit

Usage:
- System auto-sends messages
- Track open rates
- Track redemption rates''',
            },
            {
                'category': 'marketing',
                'name': 'Carbon Footprint Tracker',
                'slug': 'carbon-tracker',
                'short_description': 'Track and offset carbon per guest',
                'full_description': 'Calculate carbon footprint per stay. Offer tree planting options. Attracts eco-conscious guests.',
                'icon': 'fas fa-leaf',
                'price_type': 'monthly',
                'price': 399,
                'original_price': 799,
                'features': ['Carbon calculation', 'Tree planting option', 'Eco-certificates', 'Sustainability report', 'Guest badges'],
                'manual_title': 'How to Use Carbon Tracker',
                'manual_content': '''1. Go to Services → Carbon Tracker
2. Enable for all stays
3. Configure offset options:
   - Plant 1 tree: ₹50
   - Carbon offset: ₹100
4. Add to checkout flow

Usage:
- Stay ends → carbon calculated
- Guest sees: "Your stay: 50kg CO2"
- Option to offset
- Eco-certificates sent''',
            },
            
            # ===== SUSTAINABILITY =====
            {
                'category': 'sustainability',
                'name': 'AI Waste Management',
                'slug': 'ai-waste-management',
                'short_description': 'AI tracks and reduces food waste 50%',
                'full_description': 'AI analyzes waste patterns, suggests portion adjustments. Reduces food waste by 50%.',
                'icon': 'fas fa-trash-alt',
                'price_type': 'monthly',
                'price': 999,
                'original_price': 1999,
                'features': ['Waste tracking', 'Pattern analysis', 'Portion suggestions', 'Waste reports', 'Cost savings'],
                'manual_title': 'How to Use AI Waste Management',
                'manual_content': '''1. Go to Services → Waste Management
2. Log daily waste (or use IoT scale)
3. View AI insights:
   - "Paneer waste up 20% this week"
   - "Reduce portion size for dal"
4. Follow suggestions

Usage:
- Daily: Log waste items
- Weekly: Review AI suggestions
- Monthly: Track waste reduction''',
            },
            
            # ===== SECURITY =====
            {
                'category': 'security',
                'name': 'Biometric Check-in',
                'slug': 'biometric-checkin',
                'short_description': 'Face recognition for check-in',
                'full_description': 'Guests upload ID and photo. Face recognition verifies identity. Zero-wait check-in.',
                'icon': 'fas fa-fingerprint',
                'price_type': 'monthly',
                'price': 1499,
                'original_price': 2999,
                'features': ['Face recognition', 'ID verification', 'Zero-wait check-in', 'Security alerts', 'Guest history'],
                'manual_title': 'How to Setup Biometric Check-in',
                'manual_content': '''1. Go to Services → Biometric Check-in
2. Configure face recognition system
3. Set up camera at reception
4. Enable pre-registration:
   - Guest uploads photo online
   - Face data stored securely

Usage:
- Guest arrives
- Camera scans face
- Identity verified instantly
- Check-in complete''',
            },
            {
                'category': 'security',
                'name': 'Blockchain Traceability',
                'slug': 'blockchain-traceability',
                'short_description': 'QR shows farm-to-plate journey',
                'full_description': 'Blockchain records every ingredient source. Guests scan QR to see where their food came from.',
                'icon': 'fas fa-link',
                'price_type': 'monthly',
                'price': 1999,
                'original_price': 3999,
                'features': ['Supply chain tracking', 'Farm-to-plate info', 'QR verification', 'Trust badges', 'Premium positioning'],
                'manual_title': 'How to Setup Blockchain Traceability',
                'manual_content': '''1. Go to Services → Blockchain Traceability
2. Add suppliers with source data
3. Link ingredients to menu items
4. Enable QR display on menu

Usage:
- Guest scans dish QR
- Sees: "Paneer from Amul, Punjab"
- Harvest date, transport method
- Builds trust, justifies premium''',
            },
        ]
        
        for service_data in services:
            category = categories[service_data.pop('category')]
            features = service_data.pop('features')
            service_data['category'] = category
            service_data['features'] = features
            
            service, created = Service.objects.get_or_create(
                slug=service_data['slug'],
                defaults=service_data
            )
            if created:
                self.stdout.write(f'  [+] Created: {service.name}')
            else:
                self.stdout.write(f'  [=] Exists: {service.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\nDone! {Service.objects.count()} services available.'))
