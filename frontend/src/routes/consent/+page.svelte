<script lang="ts">
	import Seo from '$lib/components/layout/Seo.svelte';
	import { Container } from '$lib/components/ui/container';
	import { LEGAL } from '$lib/content/pages';
	import Consent from '$lib/content/legal/Consent.svelte';
</script>

<Seo title={LEGAL.consent.metaTitle} description={LEGAL.consent.description} path="/consent" />

<Container class="pt-32 pb-20">
	<div class="max-w-3xl">
		<h1 class="text-display">
			{LEGAL.consent.title}
		</h1>
		<div class="mt-8 space-y-4 leading-relaxed text-foreground/85">
			<Consent />
		</div>
	</div>
</Container>
