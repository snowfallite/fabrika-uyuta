<script lang="ts">
	import Seo from '$lib/components/layout/Seo.svelte';
	import { Container } from '$lib/components/ui/container';
	import { LEAD_PAGE, LEAD_SECTION } from '$lib/content/lead-form';
	import LeadForm from '$lib/features/lead-form/LeadForm.svelte';

	let { data, form } = $props();
</script>

<Seo title={LEAD_PAGE.metaTitle} description={LEAD_PAGE.description} path="/lead" noindex />

<Container class="grid gap-10 pt-32 pb-24 lg:grid-cols-2 lg:gap-16">
	<div>
		<h1 class="text-display">
			{LEAD_PAGE.title}
		</h1>
		<p class="mt-6 max-w-md text-lg leading-relaxed text-muted-foreground">{LEAD_SECTION.text}</p>
	</div>
	<div class="rounded-[2rem] p-7 glass md:p-10">
		<LeadForm
			idPrefix="lead-page"
			product={data.product}
			phone={data.settings.phone}
			phoneDisplay={data.settings.phone_display}
			result={form}
		/>
	</div>
</Container>
