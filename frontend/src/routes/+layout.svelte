<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import Navigation from '$lib/components/Navigation.svelte';
	import { authStore } from '$lib/stores/authStore';
	import { themeStore } from '$lib/stores/themeStore';
	import { checkAuthStatus } from '$lib/api/auth';

	let isLoading = true;

	onMount(async () => {
		// Check authentication status on app load
		await checkAuthStatus();
		isLoading = false;
	});
</script>

<svelte:head>
	<title>RePlayList - Transfer Playlists Between Spotify and YouTube</title>
	<meta name="description" content="Transfer your playlists seamlessly between Spotify and YouTube with RePlayList" />
</svelte:head>

{#if isLoading}
	<div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
		<div class="text-center">
		<div class="w-16 h-16 mx-auto mb-4">
			<img src="/static/assets/logo/svg/logo.svg" alt="RePlayList" class="w-full h-full animate-pulse" />
		</div>
			<div class="text-lg font-medium text-gray-600 dark:text-gray-300">Loading RePlayList...</div>
		</div>
	</div>
{:else}
	<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
		<Navigation />
		
		<main class="pt-16">
			<slot />
		</main>
	</div>
{/if}
