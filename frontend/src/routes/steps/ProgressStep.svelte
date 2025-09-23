<script lang="ts">
	import { transferStore } from '$lib/stores/transferStore';
	import ProgressBar from '$lib/components/ProgressBar.svelte';
</script>

<div class="text-center mb-8">
	<h2 class="text-2xl font-bold text-gray-900 dark:text-gray-text-100 mb-4">Transferring Playlist</h2>
	<p class="text-gray-600 dark:text-gray-text-200 mb-8">Please wait while we transfer your playlist...</p>
</div>

<div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 mb-8">
	{#if $transferStore.transferProgress}
		<ProgressBar
			completed={$transferStore.transferProgress.completed}
			total={$transferStore.transferProgress.total}
			status={$transferStore.transferProgress.status}
			currentTrack={$transferStore.transferProgress.current_track}
			noOpTransfer={$transferStore.noOpTransfer}
		/>
	{:else}
		<ProgressBar
			completed={0}
			total={0}
			status="pending"
			noOpTransfer={$transferStore.noOpTransfer}
		/>
	{/if}
</div>
