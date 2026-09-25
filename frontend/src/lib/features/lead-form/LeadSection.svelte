<script lang="ts">
	import { Section } from '$lib/components/ui/section';
	import { LEAD_SECTION } from '$lib/content/lead-form';
	import type { SiteSettings } from '$lib/types';
	import LeadForm from './LeadForm.svelte';

	interface Props {
		settings: SiteSettings;
	}

	let { settings }: Props = $props();
</script>

<Section id="lead" class="scroll-mt-0">
	<div class="grid items-stretch gap-10 lg:grid-cols-2 lg:gap-16">
		<div class="flex flex-col justify-center">
			<p class="mb-4 text-xs font-medium tracking-widest text-muted-foreground uppercase">
				{LEAD_SECTION.eyebrow}
			</p>
			<h2
				id="lead-title"
				class="text-4xl leading-[1.08] font-light text-balance text-primary sm:text-5xl lg:text-6xl"
			>
				{LEAD_SECTION.title}
			</h2>
			<p class="mt-6 max-w-md text-lg leading-relaxed text-muted-foreground">
				{LEAD_SECTION.text}
			</p>
		</div>
		<div class="rounded-[2rem] p-7 glass md:p-10">
			<LeadForm idPrefix="lead" phone={settings.phone} phoneDisplay={settings.phone_display} />
		</div>
	</div>
</Section>
