<script lang="ts">
	import { env } from '$env/dynamic/public';
	import { BRAND } from '$lib/content/layout';
	import { previewImage } from '$lib/domain/seo';
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
	const preview = $derived(previewImage(origin, image, title));
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
	<meta property="og:image" content={preview.url} />
	<meta property="og:image:width" content={String(preview.width)} />
	<meta property="og:image:height" content={String(preview.height)} />
	<meta property="og:image:alt" content={preview.alt} />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content={title} />
	{#if description}
		<meta name="twitter:description" content={description} />
	{/if}
	<meta name="twitter:image" content={preview.url} />
	{#if noindex}
		<meta name="robots" content="noindex" />
	{/if}
</svelte:head>
