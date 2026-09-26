<script lang="ts">
	import Check from '@lucide/svelte/icons/check';
	import { Button } from '$lib/components/ui/button';
	import { LEAD_MESSAGES } from '$lib/content/lead-form';

	interface Props {
		onagain: () => void;
	}

	let { onagain }: Props = $props();

	let message: HTMLElement | undefined = $state();

	// The form collapses into this block: focus brings it into view and lets screen readers read it.
	$effect(() => {
		message?.focus();
	});
</script>

<div
	data-lead-success
	class="flex min-h-[20rem] flex-col items-center justify-center gap-6 py-4 text-center"
>
	<span
		class="flex size-16 items-center justify-center rounded-full bg-success/10 text-success"
		aria-hidden="true"
	>
		<Check class="size-8" strokeWidth={2.25} />
	</span>
	<!-- One status region with the whole 12.2 text, shown as a heading line and a note. -->
	<div bind:this={message} role="status" tabindex="-1" class="space-y-2 outline-none">
		<p class="font-display text-3xl leading-tight text-balance text-primary">
			{LEAD_MESSAGES.successTitle}
		</p>
		<p class="text-muted-foreground">{LEAD_MESSAGES.successText}</p>
	</div>
	<Button variant="outline" size="sm" onclick={onagain}>{LEAD_MESSAGES.again}</Button>
</div>
