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
	<!-- Full screen on phones; the header with the close button stays put while the form scrolls. -->
	<!-- The close button now comes first in the DOM; focus still starts in the first field (S2-03). -->
	<Dialog.Content
		showCloseButton={false}
		onOpenAutoFocus={(event) => {
			event.preventDefault();
			document.getElementById('dialog-name')?.focus();
		}}
		class="pt-0 max-sm:inset-0 max-sm:max-h-dvh max-sm:max-w-none max-sm:translate-0 max-sm:rounded-none md:pt-0"
	>
		<Dialog.Header
			class="sticky top-0 z-10 -mx-7 flex-row items-start justify-between gap-4 bg-background px-7 pt-7 pb-2 md:-mx-10 md:px-10 md:pt-10"
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
		<LeadForm
			idPrefix="dialog"
			product={leadDialog.product}
			phone={settings.phone}
			phoneDisplay={settings.phone_display}
		/>
	</Dialog.Content>
</Dialog.Root>
