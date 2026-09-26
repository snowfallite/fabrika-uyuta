<script lang="ts">
	import { page } from '$app/state';
	import { Button } from '$lib/components/ui/button';
	import { Container } from '$lib/components/ui/container';
	import { HOME_LINK, NOT_FOUND, SERVER_ERROR } from '$lib/content/pages';

	const texts = $derived(page.status === 404 ? NOT_FOUND : SERVER_ERROR);
</script>

<svelte:head>
	<title>{texts.metaTitle}</title>
	<meta name="robots" content="noindex" />
</svelte:head>

<Container class="flex min-h-[70svh] flex-col items-start justify-center pt-32 pb-24">
	<!-- Decorative number as generated content: pale like the template, outside contrast checks. -->
	<p
		aria-hidden="true"
		data-status={page.status}
		class="font-display text-7xl font-light text-primary/40 before:content-[attr(data-status)]"
	></p>
	<h1 class="mt-4 text-display">{texts.title}</h1>
	<p class="mt-4 max-w-xl text-lg leading-relaxed text-muted-foreground">{texts.text}</p>
	<Button href="/" class="mt-9">{HOME_LINK}</Button>
</Container>
