<script lang="ts">
    import { transferStore, transferActions } from '$lib/stores/transferStore';
    import TransferDirectionSelector from '$lib/components/TransferDirectionSelector.svelte';
    import StepNav from '$lib/components/StepNav.svelte';

	// Reactive statements
	$: canProceed = $transferStore.transferDirection !== '';

    function previousStep() { transferActions.previousStep(); }
    function nextStep() { transferActions.nextStep(); }
</script>

<div class="text-center mb-8">
	<h2 class="text-2xl font-bold text-gray-900 dark:text-gray-text-100 mb-4">Choose Transfer Direction</h2>
	<p class="text-gray-600 dark:text-gray-text-200 mb-8">Select which platforms you want to transfer between</p>
</div>

<TransferDirectionSelector
	bind:selectedDirection={$transferStore.transferDirection}
/>

<div class="mt-8">
	<StepNav on:back={previousStep} on:next={nextStep} nextDisabled={!canProceed} />
</div>
