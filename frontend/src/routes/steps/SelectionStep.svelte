<script lang="ts">
	import { transferStore, transferActions } from '$lib/stores/transferStore';
	import { playlistStore } from '$lib/stores/playlistStore';
	import { playlistService } from '$lib/services/playlistService';
	import SourceSelector from '$lib/components/SourceSelector.svelte';
	import TargetSelector from '$lib/components/TargetSelector.svelte';
	import StepNav from '$lib/components/StepNav.svelte';
	import { useResponsive } from '$lib/composables/useResponsive';
	import { createStaggerAnimation } from '$lib/composables/useAnimations';

	const { isMobile, isTablet } = useResponsive();
	const staggerAnimation = createStaggerAnimation(100);

	// Reactive statements
	$: canProceed = $transferStore.selectedSourcePlaylist !== null && 
		($transferStore.selectedTargetPlaylist !== null || 
		 ($transferStore.targetActiveTab === 'new' && !!$transferStore.customPlaylistName.trim()));

	async function refreshPlaylists() {
		await playlistService.refreshPlaylists();
	}

	function previousStep() {
		transferActions.previousStep();
	}

	function nextStep() {
		transferActions.nextStep();
	}
</script>

<div class="text-center mb-8">
	<div class="flex items-center justify-center gap-4 mb-4">
		<h2 class="text-2xl font-bold text-gray-900 dark:text-gray-text-100">Select Playlists</h2>
		<button
			on:click={refreshPlaylists}
			disabled={$playlistStore.isRefreshing}
			class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg transition-colors duration-200 disabled:cursor-not-allowed"
		>
			<svg 
				class="w-4 h-4 transition-transform duration-500 {$playlistStore.isRefreshing ? 'animate-spin' : ''}" 
				fill="none" 
				stroke="currentColor" 
				viewBox="0 0 24 24"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
			</svg>
			<span>{$playlistStore.isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
		</button>
	</div>
	<p class="text-gray-600 dark:text-gray-text-200 mb-8">Choose your source playlist and destination</p>
</div>

<div 
	class="grid gap-6 mb-8 w-full {$isMobile ? 'grid-cols-1' : $isTablet ? 'grid-cols-1' : 'grid-cols-2'}"
	role="region"
	aria-label="Playlist selection"
>
	<div in:staggerAnimation={{ index: 0 }}>
		<SourceSelector />
	</div>
	<div in:staggerAnimation={{ index: 1 }}>
		<TargetSelector />
	</div>
</div>

<StepNav on:back={previousStep} on:next={nextStep} nextDisabled={!canProceed} />
