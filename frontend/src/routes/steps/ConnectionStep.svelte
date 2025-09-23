<script lang="ts">
    import { authStore } from '$lib/stores/authStore';
    import { transferActions } from '$lib/stores/transferStore';
    import { authService } from '$lib/services/authService';
    import StepNav from '$lib/components/StepNav.svelte';

	// Reactive statements
	$: canProceed = $authStore.spotify || $authStore.youtube;

	async function handleAuth(platform: 'spotify' | 'youtube') {
		await authService.handleAuth(platform);
	}

	async function handleDisconnect(platform: 'spotify' | 'youtube') {
		await authService.handleDisconnect(platform);
	}

	function nextStep() {
		transferActions.nextStep();
	}
</script>

<div class="text-center mb-8">
	<h2 class="text-2xl font-bold text-gray-900 dark:text-gray-text-100 mb-4">Connect to Platforms</h2>
	<p class="text-gray-600 dark:text-gray-text-200 mb-8">Connect to Spotify and/or YouTube to start transferring playlists</p>
</div>

<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
	<!-- Spotify Connection -->
	<div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-white/10 p-6 transition-all duration-300 hover:shadow-lg hover:scale-105">
		<div class="flex items-center justify-between">
			<div class="flex items-center space-x-3">
				<div class="w-10 h-10 bg-spotify-500 rounded-lg flex items-center justify-center">
					<img src="/static/assets/icons/spotify_icon.svg" alt="Spotify" class="w-6 h-6" />
				</div>
				<div>
					<h3 class="text-lg font-semibold text-gray-900 dark:text-gray-text-100">Spotify</h3>
					<p class="text-sm text-gray-500 dark:text-gray-text-200">
						{$authStore.spotify ? 'Connected' : 'Not connected'}
					</p>
				</div>
			</div>
			<button
				on:click={() => $authStore.spotify ? handleDisconnect('spotify') : handleAuth('spotify')}
				class="px-4 py-2 rounded-lg font-medium transition-colors duration-200 {$authStore.spotify 
					? 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-500' 
					: 'bg-spotify-500 hover:bg-spotify-600 text-black'}"
			>
				{$authStore.spotify ? 'Disconnect' : 'Connect'}
			</button>
		</div>
	</div>

	<!-- YouTube Connection -->
	<div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-white/10 p-6 transition-all duration-300 hover:shadow-lg hover:scale-105">
		<div class="flex items-center justify-between">
			<div class="flex items-center space-x-3">
				<div class="w-10 h-10 bg-youtube-500 rounded-lg flex items-center justify-center">
					<img src="/static/assets/icons/youtube_icon.svg" alt="YouTube" class="w-6 h-6" />
				</div>
				<div>
					<h3 class="text-lg font-semibold text-gray-900 dark:text-gray-text-100">YouTube</h3>
					<p class="text-sm text-gray-500 dark:text-gray-text-200">
						{$authStore.youtube ? 'Connected' : 'Not connected'}
					</p>
				</div>
			</div>
			<button
				on:click={() => $authStore.youtube ? handleDisconnect('youtube') : handleAuth('youtube')}
				class="px-4 py-2 rounded-lg font-medium transition-colors duration-200 {$authStore.youtube 
					? 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-500' 
					: 'bg-youtube-500 hover:bg-youtube-600 text-white'}"
			>
				{$authStore.youtube ? 'Disconnect' : 'Connect'}
			</button>
		</div>
	</div>
</div>

<div>
    <StepNav showBack={false} on:next={nextStep} nextDisabled={!canProceed} />
</div>
