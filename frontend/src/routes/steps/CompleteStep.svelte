<script lang="ts">
	import { transferStore, sourcePlatform, targetPlatform } from '$lib/stores/transferStore';
	import { playlistStore } from '$lib/stores/playlistStore';
	import { playlistService } from '$lib/services/playlistService';
	import { transferService } from '$lib/services/transferService';
	import { CheckCircle, ArrowRight } from 'lucide-svelte';
	import TransferSummary from '$lib/components/TransferSummary.svelte';

	async function refreshPlaylists() {
		await playlistService.refreshPlaylists();
	}

	function startNewTransfer() {
		transferService.startNewTransfer();
	}
</script>

<div class="text-center mb-8">
	<div class="flex items-center justify-center gap-4 mb-4">
		<h2 class="text-2xl font-bold text-gray-900 dark:text-gray-text-100">Transfer Complete!</h2>
		<button
			on:click={refreshPlaylists}
			disabled={$playlistStore.isRefreshing}
			class="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white rounded-lg transition-colors duration-200 disabled:cursor-not-allowed"
		>
			<svg 
				class="w-4 h-4 transition-transform duration-500 {$playlistStore.isRefreshing ? 'animate-spin' : ''}" 
				fill="none" 
				stroke="currentColor" 
				viewBox="0 0 24 24"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
			</svg>
			<span>{$playlistStore.isRefreshing ? 'Refreshing...' : 'Refresh Lists'}</span>
		</button>
	</div>
	<p class="text-gray-600 dark:text-gray-text-200 mb-8">Your playlist has been successfully transferred</p>
</div>

<div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 mb-8">
	<div class="text-center">
		<div class="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
			<CheckCircle class="w-8 h-8 text-white" />
		</div>
		<h3 class="text-lg font-semibold text-gray-900 dark:text-gray-text-100 mb-2">
			Transfer Successful!
		</h3>
		<p class="text-gray-500 dark:text-gray-text-200 mb-6">
			Your playlist has been successfully transferred from {$sourcePlatform === 'spotify' ? 'Spotify' : 'YouTube'} to {$targetPlatform === 'spotify' ? 'Spotify' : 'YouTube'}
		</p>
		
		{#if $transferStore.transferSummary}
			<TransferSummary summary={$transferStore.transferSummary} />
		{/if}
	</div>
</div>

<!-- Step Navigation -->
<div class="flex justify-center">
	<button
		on:click={startNewTransfer}
		class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors duration-200 flex items-center space-x-2"
	>
		<span>Start New Transfer</span>
		<ArrowRight class="w-4 h-4" />
	</button>
</div>
