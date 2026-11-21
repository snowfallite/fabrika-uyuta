<script lang="ts">
	import Seo from '$lib/components/layout/Seo.svelte';
	import { Container } from '$lib/components/ui/container';
	import { LEGAL } from '$lib/content/pages';
	import Cookies from '$lib/content/legal/Cookies.svelte';
</script>

<Seo title={LEGAL.cookies.metaTitle} description={LEGAL.cookies.description} path="/cookies" />

<Container class="pt-32 pb-20">
	<div class="max-w-3xl">
		<h1 class="text-display">
			{LEGAL.cookies.title}
		</h1>
		<div class="mt-8 space-y-4 leading-relaxed text-foreground/85">
			<Cookies />
		</div>
	</div>
</Container>
