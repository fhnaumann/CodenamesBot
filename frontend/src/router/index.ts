import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import GamesView from '@/views/GamesView.vue'
import PlayersView from '@/views/PlayersView.vue'
import QueryView from '@/views/QueryView.vue'
import AdminView from '@/views/AdminView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/games',
      name: 'games',
      component: GamesView,
    },
    {
      path: '/players',
      name: 'players',
      component: PlayersView,
    },
    {
      path: '/query',
      name: 'query',
      component: QueryView,
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
    },
  ],
})

export default router
