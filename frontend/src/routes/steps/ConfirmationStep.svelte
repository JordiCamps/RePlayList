<script lang="ts">
	import { transferStore, transferActions, sourcePlatform, targetPlatform } from '$lib/stores/transferStore';
	import { transferService } from '$lib/services/transferService';
	import StepNav from '$lib/components/StepNav.svelte';
	import { ArrowRight } from 'lucide-svelte';

	// Reactive statements
	$: canTransfer = $transferStore.selectedSourcePlaylist && (
		$transferStore.selectedTargetPlaylist || 
		($transferStore.targetActiveTab === 'new' && !!$transferStore.customPlaylistName.trim())
	);

	function previousStep() {
		transferActions.previousStep();
	}

	async function handleTransfer() {
		const transferData = {
			source: {
				platform: $transferStore.selectedSourcePlaylist!.platform,
				playlist_id: $transferStore.selectedSourcePlaylist!.id
			},
			target: {
				platform: $targetPlatform,
				playlist_id: $transferStore.targetActiveTab === 'existing' && $transferStore.selectedTargetPlaylist 
					? $transferStore.selectedTargetPlaylist.id 
					: undefined
			},
			mode: ($transferStore.targetActiveTab === 'new' ? 'new_playlist' : 'append') as 'new_playlist' | 'append',
			custom_playlist_name: $transferStore.targetActiveTab === 'new' ? $transferStore.customPlaylistName : undefined
		};

		await transferService.startTransfer(transferData);
	}
</script>

<div class="text-center mb-8">
	<h2 class="text-2xl font-bold text-gray-900 dark:text-gray-text-100 mb-4">Confirm Transfer</h2>
	<p class="text-gray-600 dark:text-gray-text-200 mb-8">Review your transfer details before proceeding</p>
</div>

<div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 mb-8">
	<div class="flex items-center justify-center space-x-8">
		<!-- Source -->
		<div class="text-center">
			<div class="w-16 h-16 bg-{$sourcePlatform}-500 rounded-xl flex items-center justify-center mx-auto mb-4">
				<img src="/static/assets/icons/{$sourcePlatform}_icon.svg" alt={$sourcePlatform} class="w-8 h-8" />
			</div>
			<h3 class="font-semibold text-gray-900 dark:text-gray-text-100 mb-2">
				{$transferStore.selectedSourcePlaylist?.name}
			</h3>
			<p class="text-sm text-gray-500 dark:text-gray-text-200">
				{$transferStore.selectedSourcePlaylist?.tracks_count ?? 0} songs
			</p>
		</div>

		<!-- Arrow -->
		<ArrowRight class="w-8 h-8 text-gray-400" />

		<!-- Target -->
		<div class="text-center">
			<div class="w-16 h-16 bg-{$targetPlatform}-500 rounded-xl flex items-center justify-center mx-auto mb-4">
				<img src="/static/assets/icons/{$targetPlatform}_icon.svg" alt={$targetPlatform} class="w-8 h-8" />
			</div>
			<h3 class="font-semibold text-gray-900 dark:text-gray-text-100 mb-2">
				{$transferStore.targetActiveTab === 'new' ? $transferStore.customPlaylistName : $transferStore.selectedTargetPlaylist?.name}
			</h3>
			<p class="text-sm text-gray-500 dark:text-gray-text-200">
				{$transferStore.targetActiveTab === 'new' ? 'New Playlist' : `${$transferStore.selectedTargetPlaylist?.tracks_count ?? 0} songs`}
			</p>
		</div>
	</div>
</div>

<StepNav on:back={previousStep} on:next={handleTransfer} nextLabel="Start Transfer" nextDisabled={!canTransfer} />
