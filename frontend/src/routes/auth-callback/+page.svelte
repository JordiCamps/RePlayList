<script lang="ts">
	import { onMount } from 'svelte';
	import { handleAuthCallback } from '$lib/api/auth';

	onMount(async () => {
		const urlParams = new URLSearchParams(window.location.search);
		const code = urlParams.get('code');
		const success = urlParams.get('success');
		const error = urlParams.get('error');
		const platform = urlParams.get('platform') as 'spotify' | 'youtube';

		console.log('Auth callback received:', { code, success, error, platform });

		if (error) {
			// Send error to parent window
			if (window.opener) {
				window.opener.postMessage({
					type: 'AUTH_ERROR',
					platform: platform,
					error: error
				}, window.location.origin);
			}
			window.close();
			return;
		}

		if (success === 'true' && platform) {
			// Authentication was successful on backend
			// Store token and update auth status
			localStorage.setItem(`${platform}_token`, 'authenticated');
			
			// Send success message to parent window
			if (window.opener) {
				window.opener.postMessage({
					type: 'AUTH_SUCCESS',
					platform: platform
				}, window.location.origin);
			}
			window.close();
			return;
		}

		if (code && platform) {
			// Fallback: handle code exchange directly
			try {
				const result = await handleAuthCallback(platform, code);
				if (result.success) {
					// Success message is already sent by handleAuthCallback
					window.close();
				} else {
					// Error message is already sent by handleAuthCallback
					window.close();
				}
			} catch (error) {
				// Send error to parent window
				if (window.opener) {
					window.opener.postMessage({
						type: 'AUTH_ERROR',
						platform: platform,
						error: error instanceof Error ? error.message : 'Unknown error'
					}, window.location.origin);
				}
				window.close();
			}
		} else {
			// Send error to parent window
			if (window.opener) {
				window.opener.postMessage({
					type: 'AUTH_ERROR',
					platform: platform,
					error: 'Missing authorization code or platform'
				}, window.location.origin);
			}
			window.close();
		}
	});
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
	<div class="text-center">
		<div class="w-16 h-16 mx-auto mb-4">
			<div class="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
		</div>
		<div class="text-lg font-medium text-gray-600 dark:text-gray-300">Completing authentication...</div>
	</div>
</div>
