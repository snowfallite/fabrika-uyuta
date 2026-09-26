<script lang="ts">
	import { env } from '$env/dynamic/public';
	import { BRAND } from '$lib/content/layout';
	import { absoluteUrl } from '$lib/domain/url';
	import type { ImageAsset } from '$lib/types';

	interface Props {
		title: string;
		description: string;
		path: string;
		image?: ImageAsset | null;
		noindex?: boolean;
	}

	let { title, description, path, image = null, noindex = false }: Props = $props();

	const origin = $derived(env.PUBLIC_SITE_URL ?? '');
	const canonical = $derived(absoluteUrl(origin, path));
</script>

<svelte:head>
	<title>{title}</title>
	{#if description}
		<meta name="description" content={description} />
		<meta property="og:description" content={description} />
	{/if}
	<link rel="canonical" href={canonical} />
	<meta property="og:type" content="website" />
	<meta property="og:site_name" content={BRAND} />
	<meta property="og:locale" content="ru_RU" />
	<meta property="og:title" content={title} />
	<meta property="og:url" content={canonical} />
	{#if image}
		<meta property="og:image" content={absoluteUrl(origin, image.url)} />
		<meta property="og:image:width" content={String(image.width)} />
		<meta property="og:image:height" content={String(image.height)} />
		<meta property="og:image:alt" content={image.alt} />
	{/if}
	{#if noindex}
		<meta name="robots" content="noindex" />
	{/if}
</svelte:head>
