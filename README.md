# BrewNest Order Platform

A full-stack coffee shop ordering system built with React, FastAPI, PostgreSQL, MongoDB, Docker, WebSocket, and Razorpay Test Mode.

## Project Overview

BrewNest allows customers to:

- Browse the coffee shop menu
- Customize items using modifiers
- Add items to the cart
- Place an order
- Pay using Razorpay Test Mode
- Track order status live
- Cancel an eligible order

Baristas can:

- See only paid orders
- Start preparing an order
- Mark an order as ready
- Cancel an order after preparation starts with a reason

## Technology Stack

### Frontend
- React
- Vite
- JavaScript
- CSS

### Backend
- Python
- FastAPI
- SQLAlchemy

### Databases
- PostgreSQL - orders, order items, payments
- MongoDB - menu and modifiers

### Payment
- Razorpay Test Mode
- Razorpay Checkout
- Signed Razorpay webhook

### Real-time Updates
- WebSocket

### Deployment
- Docker
- Docker Compose

## Architecture

```text
Customer Kiosk
     |
     | REST API
     v
   FastAPI
     |
     +--------------------+
     |                    |
     v                    v
PostgreSQL             MongoDB
Orders                 Menu
Payments               Modifiers
     |
     v
Razorpay
     |
     | Signed Webhook
     v
FastAPI
     |
     | WebSocket
     +--------------------+
     |                    |
     v                    v
Barista Screen      Customer Status

## Required Design Questions

### How does a live ticket update reach the right screens - and what breaks once you run more than one backend worker process?

BrewNest uses WebSockets for real-time communication between the FastAPI backend and the React customer and barista screens.

There are two WebSocket endpoints:

- Customer: `/ws/orders/{order_id}`
- Barista: `/ws/barista`

When a customer tracks an order, the React application opens a WebSocket connection using the order ID. For example:

```text
/ws/orders/15



### This becomes a 20-location chain tomorrow. What in your design changes first?

The first major design change would be introducing a `Location` entity and making the existing data and APIs location-aware.

The current BrewNest design is centered around a single coffee shop. When the system expands to 20 locations, each order and operational activity must be associated with a specific location.

A simplified design would become:

```text
Location
   |
   +---- Orders
   |
   +---- Payments
   |
   +---- Menu
   |
   +---- Barista operations


### What actually stops a duplicate Razorpay webhook from charging or ticketing the same order twice?

BrewNest does not use the frontend payment response as the final confirmation of payment. Payment confirmation is handled through Razorpay's signed webhook.

When a `payment.captured` webhook is received, the backend performs the following steps:

1. It verifies the Razorpay webhook signature.
2. It extracts the Razorpay order ID and payment ID from the webhook.
3. It finds the corresponding payment record in PostgreSQL.
4. It checks whether that payment has already been processed.
5. If the payment is not already processed, the backend stores the Razorpay payment ID, changes the payment status to `PAID`, and changes the related order status to `PAID`.
6. Only after this successful processing does the backend send the paid-order event to the barista screen through WebSocket.

For the first webhook:

```text
Razorpay
   ↓
payment.captured
   ↓
Verify webhook signature
   ↓
Find payment record
   ↓
Payment is not yet PAID
   ↓
Payment → PAID
   ↓
Order → PAID
   ↓
Send ticket to barista