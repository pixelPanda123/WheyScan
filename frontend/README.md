# WheyScan Frontend

React, TypeScript, TanStack Start, and Tailwind CSS frontend for WheyScan.

WheyScan displays whey protein products matched across Indian retailers. Users can search and filter products, review each retailer's MRP and price per 100g, and open the retailer listing directly.

## Backend API

The frontend reads from the existing FastAPI backend:

```sh
GET http://localhost:8001/discovery/search
```

Set a different backend URL with:

```sh
VITE_API_BASE_URL=http://localhost:8001
```

No mock product data is used by the frontend.

## Development

```sh
npm install
npm run dev
```

## Checks

```sh
npm run build
npm run lint
```
