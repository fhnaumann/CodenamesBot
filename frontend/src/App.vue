<script setup lang="ts">
import { useRoute } from 'vue-router'
import { Separator } from '@/components/ui/separator'

const route = useRoute()
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="border-b">
      <div class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-8">
            <router-link to="/" class="text-2xl font-bold tracking-tight hover:opacity-80">
              Codenames Stats
            </router-link>

            <nav class="hidden md:flex items-center gap-6">
              <router-link
                to="/"
                class="text-sm font-medium transition-colors hover:text-primary"
                :class="route.path === '/' ? 'text-primary' : 'text-muted-foreground'"
              >
                Home
              </router-link>
              <router-link
                to="/games"
                class="text-sm font-medium transition-colors hover:text-primary"
                :class="route.path === '/games' ? 'text-primary' : 'text-muted-foreground'"
              >
                Games
              </router-link>
              <router-link
                to="/players"
                class="text-sm font-medium transition-colors hover:text-primary"
                :class="route.path === '/players' ? 'text-primary' : 'text-muted-foreground'"
              >
                Leaderboards
              </router-link>
              <router-link
                to="/query"
                class="text-sm font-medium transition-colors hover:text-primary"
                :class="route.path === '/query' ? 'text-primary' : 'text-muted-foreground'"
              >
                Custom Query
              </router-link>
              <router-link
                to="/admin"
                class="text-sm font-medium transition-colors hover:text-primary"
                :class="route.path === '/admin' ? 'text-primary' : 'text-muted-foreground'"
              >
                Admin
              </router-link>
            </nav>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <RouterView />
    </main>

    <!-- Footer -->
    <footer class="border-t mt-12">
      <div class="container mx-auto px-4 py-6">
        <p class="text-center text-sm text-muted-foreground">
          Codenames Statistics Dashboard - Track your game performance
        </p>
      </div>
    </footer>
  </div>
</template>
