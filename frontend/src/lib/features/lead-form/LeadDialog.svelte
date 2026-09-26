<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import { LEAD_PAGE, LEAD_SECTION } from '$lib/content/lead-form';
	import type { SiteSettings } from '$lib/types';
	import { leadDialog } from './dialog.svelte';
	import LeadForm from './LeadForm.svelte';

	interface Props {
		settings: SiteSettings;
	}

	let { settings }: Props = $props();
</script>

<!-- Content mounts on open, so every opening starts with a clean form. -->
<Dialog.Root bind:open={leadDialog.isOpen}>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>{LEAD_PAGE.title}</Dialog.Title>
			<Dialog.Description class="text-muted-foreground">{LEAD_SECTION.text}</Dialog.Description>
		</Dialog.Header>
		<LeadForm
			idPrefix="dialog"
			product={leadDialog.product}
			phone={settings.phone}
			phoneDisplay={settings.phone_display}
		/>
	</Dialog.Content>
</Dialog.Root>
