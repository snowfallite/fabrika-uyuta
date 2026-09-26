<script lang="ts">
	import { Section } from '$lib/components/ui/section';
	import { LEAD_SECTION } from '$lib/content/lead-form';
	import type { ProductKind, SiteSettings } from '$lib/types';
	import LeadForm from './LeadForm.svelte';

	interface Props {
		settings: SiteSettings;
		/** Section anchor; the category page uses its own. */
		id?: string;
		idPrefix?: string;
		product?: ProductKind | '';
	}

	let { settings, id = 'lead', idPrefix = 'lead', product = '' }: Props = $props();
</script>

<Section {id} class="scroll-mt-0">
	<div class="grid gap-8 lg:grid-cols-2 lg:gap-16">
		<!-- Pinned next to the form instead of centred on it: no empty band above the heading. -->
		<div class="lg:sticky lg:top-32 lg:self-start">
			<p class="mb-4 text-xs font-medium tracking-widest text-muted-foreground uppercase">
				{LEAD_SECTION.eyebrow}
			</p>
			<h2
				id="{id}-title"
				class="text-4xl leading-[1.08] font-light text-balance text-primary sm:text-5xl lg:text-6xl"
			>
				{LEAD_SECTION.title}
			</h2>
			<p class="mt-5 max-w-md text-lg leading-relaxed text-muted-foreground">
				{LEAD_SECTION.text}
			</p>
		</div>
		<div class="rounded-[2rem] p-6 glass md:p-10">
			<LeadForm {idPrefix} {product} phone={settings.phone} phoneDisplay={settings.phone_display} />
		</div>
	</div>
</Section>
