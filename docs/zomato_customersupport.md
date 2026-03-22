# Zomato: Customer Support & Refund Logic

## Missing Item Protocol
If a customer reports a missing item, the support bot must first verify the "Kitchen Preparation Photo" uploaded by the restaurant. If the item is missing in the photo, an **instant refund** to Zomato Money is issued.

## Delivery Delay Compensation
For orders delayed by more than **20 minutes** beyond the "Max ETA," customers are automatically eligible for a "Delay Discount" coupon worth 20% of their next order value.

## Order Cancellation
Users can cancel an order within **60 seconds** of placement for a full refund. After 60 seconds, a cancellation fee of ₹50 is deducted to compensate the restaurant for started preparations.