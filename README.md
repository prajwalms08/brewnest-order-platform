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