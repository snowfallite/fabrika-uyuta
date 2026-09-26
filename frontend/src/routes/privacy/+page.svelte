<script lang="ts">
	import Seo from '$lib/components/layout/Seo.svelte';
	import { Container } from '$lib/components/ui/container';
	import { LEGAL } from '$lib/content/pages';
	import Privacy from '$lib/content/legal/Privacy.svelte';
</script>

<Seo title={LEGAL.privacy.metaTitle} description={LEGAL.privacy.description} path="/privacy" />

<Container class="pt-32 pb-20">
	<div class="max-w-3xl">
		<h1 class="text-display">
			{LEGAL.privacy.title}
		</h1>
		<div class="mt-8 space-y-4 leading-relaxed text-foreground/85">
			<Privacy />
		</div>
	</div>
</Container>
