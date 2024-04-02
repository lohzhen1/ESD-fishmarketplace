import { createRouter, createWebHistory } from 'vue-router'
import MarketplaceView from '../views/MarketplaceView.vue'
import OrderDetailsView from '../views/OrderDetailsView.vue'
import CartView from '../views/CartView.vue'
import LoginView from '../views/LoginView.vue'
import SuccessView from '../views/SuccessView.vue'
import InventoryView from '../views/InventoryView.vue'
import DeliveryView from '../views/DeliveryView.vue'
import AuctionView from '../views/AuctionView.vue'
import CancelledView from '../views/CancelledView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'marketplace',
      component: MarketplaceView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/success',
      name: 'success',
      component: SuccessView
    },
    {
      path: '/cancelled',
      name: 'cancelled',
      component: CancelledView
    },
    {
      path: '/inventory',
      name: 'inventory',
      component: InventoryView
    },
    {
      path: '/auction',
      name: 'auction',
      component: AuctionView
    },
    {
      path: '/delivery',
      name: 'delivery',
      component: DeliveryView
    },
    {
      path: '/accountdetails',
      name: 'accountdetails',
      component: () => import('../views/AccountDetailsView.vue')
    },
    {
      path: '/displayallorders',
      name: 'displayallorders',
      component: () => import('../views/DisplayAllOrdersView.vue')
    },
    {
      path: '/displayallorders',
      name: 'displayallorders',
      component: () => import('../views/DisplayAllOrdersView.vue')
    },
    {
      path: '/refunddetails/:supplierId',
      name: 'refunddetails',
      component: () => import('../views/RefundDetails.vue')
    },


    {
      path: '/orderdetails',
      name: 'orderdetails',
      component: OrderDetailsView
    },
    {
      path: '/cart',
      name: 'cart',
      component: CartView
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue')
    }
  ]
})

export default router
