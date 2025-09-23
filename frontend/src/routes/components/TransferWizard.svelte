<script lang="ts">
	import { onMount } from 'svelte';
	import { transferStore, transferActions, canTransfer } from '$lib/stores/transferStore';
	import { authStore } from '$lib/stores/authStore';
	import { playlistService } from '$lib/services/playlistService';
	import { authService } from '$lib/services/authService';
	import ConnectionStep from '../steps/ConnectionStep.svelte';
	import DirectionStep from '../steps/DirectionStep.svelte';
	import SelectionStep from '../steps/SelectionStep.svelte';
	import ConfirmationStep from '../steps/ConfirmationStep.svelte';
	import ProgressStep from '../steps/ProgressStep.svelte';
	import CompleteStep from '../steps/CompleteStep.svelte';
	import Stepper from '$lib/components/Stepper.svelte';
	import { AlertCircle } from 'lucide-svelte';
	import { animations } from '$lib/composables/useAnimations';
	import NotificationSystem from '$lib/components/NotificationSystem.svelte';

	const steps = [
		{ id: 'connection', title: 'Connect Platforms' },
		{ id: 'direction', title: 'Choose Direction' },
		{ id: 'selection', title: 'Select Playlists' },
		{ id: 'confirmation', title: 'Confirm Transfer' },
		{ id: 'progress', title: 'Transferring' },
		{ id: 'complete', title: 'Complete' }
	];


	// Reactive statements
	$: canProceedFromConnection = $authStore.spotify || $authStore.youtube;
	$: canProceedFromSelection = $transferStore.selectedSourcePlaylist !== null && 
		($transferStore.selectedTargetPlaylist !== null || 
		 ($transferStore.targetActiveTab === 'new' && !!$transferStore.customPlaylistName.trim()));

	// Go back to step 1 if user disconnects from all platforms
	$: if ($transferStore.currentStep !== 'connection' && !$authStore.spotify && !$authStore.youtube) {
		transferActions.setStep('connection');
		transferActions.clearSelection();
	}

	onMount(async () => {
		await authService.checkAuthStatus();
		await playlistService.loadPlaylists();
	});
</script>

<svelte:head>
	<title>RePlayList - Transfer Playlists Between Spotify and YouTube</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<!-- Header -->
	{#if $transferStore.currentStep === 'connection'}
		<div class="text-center mb-12 pt-8">
			<h1 class="text-4xl font-bold text-gray-900 dark:text-gray-text-100 mb-4">
				Transfer Playlists Between
				<span class="branded-spotify">Spotify</span> and <span class="branded-youtube">YouTube</span>
			</h1>
			<p class="text-xl text-gray-600 dark:text-gray-text-200 max-w-2xl mx-auto">
				Seamlessly move your music playlists between platforms with just a few clicks
			</p>
		</div>
	{/if}

	<!-- Error Message -->
	{#if $transferStore.error}
		<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
			<div class="flex items-center">
				<AlertCircle class="w-5 h-5 text-red-600 mr-2" />
				<span class="text-red-800">{$transferStore.error}</span>
			</div>
		</div>
	{/if}

	<!-- Step Content -->
	<div class="max-w-7xl mx-auto min-h-[60vh] flex flex-col justify-center">
		<div class="transition-all duration-500 ease-in-out">
			{#key $transferStore.currentStep}
				<div 
					in:animations.pageIn 
					out:animations.pageOut 
					class="transform transition-all duration-300"
					role="main"
					aria-live="polite"
					aria-label="Transfer step content"
				>
					{#if $transferStore.currentStep === 'connection'}
						<ConnectionStep />
					{:else if $transferStore.currentStep === 'direction'}
						<DirectionStep />
					{:else if $transferStore.currentStep === 'selection'}
						<SelectionStep />
					{:else if $transferStore.currentStep === 'confirmation'}
						<ConfirmationStep />
					{:else if $transferStore.currentStep === 'progress'}
						<ProgressStep />
					{:else if $transferStore.currentStep === 'complete'}
						<CompleteStep />
					{/if}
				</div>
			{/key}
		</div>
	</div>

	<!-- Stepper - Show below content for steps 2+ -->
	{#if $transferStore.currentStep !== 'connection'}
		<div class="mt-12 flex justify-center">
			<div class="max-w-4xl w-full">
				<Stepper currentStep={$transferStore.currentStep} {steps} />
			</div>
		</div>
	{/if}
</div>

<!-- Notification System -->
<NotificationSystem />
