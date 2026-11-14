<script lang="ts">
	import X from '@lucide/svelte/icons/x';
	import { buttonVariants } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import { LEAD_PAGE, LEAD_SECTION } from '$lib/content/lead-form';
	import { WORKS } from '$lib/content/home';
	import type { SiteSettings } from '$lib/types';
	import { cn } from '$lib/utils';
	import { leadDialog } from './dialog.svelte';
	import LeadForm from './LeadForm.svelte';

	interface Props {
		settings: SiteSettings;
	}

	let { settings }: Props = $props();
</script>

<!-- Content mounts on open, so every opening starts with a clean form. -->
<Dialog.Root bind:open={leadDialog.isOpen}>
	<!--
		Two rows: the heading stays put, the form gets the rest. The form is wide enough
		for two columns (LeadForm, @xl), so on a desktop it fits without a scrollbar; on a
		short window only the form area scrolls. Full screen on phones.
		The close button comes first in the DOM; focus still starts in the first field (S2-03).
	-->
	<Dialog.Content
		showCloseButton={false}
		onOpenAutoFocus={(event) => {
			event.preventDefault();
			document.getElementById('dialog-name')?.focus();
		}}
		class="grid-rows-[auto_minmax(0,1fr)] gap-0 overflow-x-hidden overflow-y-hidden p-0 max-sm:inset-0 max-sm:max-h-dvh max-sm:max-w-none max-sm:translate-0 max-sm:rounded-none sm:max-w-3xl md:p-0 [&:has([data-lead-success])_[data-slot=dialog-description]]:hidden"
	>
		<Dialog.Header
			class="flex-row items-start justify-between gap-4 border-b border-border/60 px-7 pt-7 pb-5 md:px-10 md:pt-8"
		>
			<div class="flex flex-col gap-2">
				<Dialog.Title>{LEAD_PAGE.title}</Dialog.Title>
				<Dialog.Description class="text-muted-foreground">{LEAD_SECTION.text}</Dialog.Description>
			</div>
			<Dialog.Close
				class={cn(buttonVariants({ variant: 'ghost', size: 'icon' }), '-mt-1 -mr-2 shrink-0')}
				aria-label={WORKS.close}
			>
				<X class="size-5" aria-hidden="true" />
			</Dialog.Close>
		</Dialog.Header>
		<!-- Scrolls only when the window is too short; a slim scrollbar in the border colour. -->
		<div
			class="[scrollbar-width:thin] [scrollbar-color:var(--border)_transparent] overflow-y-auto overscroll-contain px-7 py-7 md:px-10 md:py-8"
		>
			<LeadForm
				idPrefix="dialog"
				product={leadDialog.product}
				phone={settings.phone}
				phoneDisplay={settings.phone_display}
			/>
		</div>
	</Dialog.Content>
</Dialog.Root>
