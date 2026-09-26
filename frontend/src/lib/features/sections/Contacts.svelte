<script lang="ts">
	import ArrowUpRight from '@lucide/svelte/icons/arrow-up-right';
	import Clock from '@lucide/svelte/icons/clock';
	import Mail from '@lucide/svelte/icons/mail';
	import MapPin from '@lucide/svelte/icons/map-pin';
	import Phone from '@lucide/svelte/icons/phone';
	import { Button } from '$lib/components/ui/button';
	import { Section } from '$lib/components/ui/section';
	import { CONTACTS } from '$lib/content/home';
	import { openFromLink } from '$lib/features/lead-form/dialog.svelte';
	import type { SiteSettings } from '$lib/types';

	interface Props {
		settings: SiteSettings;
	}

	let { settings }: Props = $props();

	const card = 'glass rounded-[1.5rem] p-6';
	const label = 'mb-1.5 text-xs font-medium tracking-widest text-muted-foreground uppercase';
	// Sans for data: phone digits and hours stay legible and easy to copy.
	const value = 'text-lg font-medium break-words text-primary';
</script>

<Section id="contacts" title={CONTACTS.title} subtitle={CONTACTS.eyebrow} tone="muted">
	<p class="-mt-4 mb-8 max-w-xl leading-relaxed text-muted-foreground">{CONTACTS.text}</p>
	<!-- Empty settings fields hide their cards (tech.md, S2-10 AC3). -->
	<ul class="grid gap-4 sm:grid-cols-2 md:gap-6 lg:grid-cols-4">
		{#if settings.phone}
			<li class={card}>
				<Phone class="mb-4 size-6 text-primary" aria-hidden="true" />
				<p class={label}>{CONTACTS.phone}</p>
				<a href="tel:{settings.phone}" class="{value} hover:underline">{settings.phone_display}</a>
			</li>
		{/if}
		{#if settings.email}
			<li class={card}>
				<Mail class="mb-4 size-6 text-primary" aria-hidden="true" />
				<p class={label}>{CONTACTS.email}</p>
				<a href="mailto:{settings.email}" class="{value} hover:underline">{settings.email}</a>
			</li>
		{/if}
		{#if settings.address}
			<li class={card}>
				<MapPin class="mb-4 size-6 text-primary" aria-hidden="true" />
				<p class={label}>{CONTACTS.address}</p>
				<p class={value}>{settings.address}</p>
				{#if settings.map_url}
					<a
						href={settings.map_url}
						class="mt-1 inline-block py-2 text-sm font-medium text-primary underline underline-offset-2"
						rel="noopener external"
						target="_blank">{CONTACTS.map}</a
					>
				{/if}
			</li>
		{/if}
		{#if settings.work_hours}
			<li class={card}>
				<Clock class="mb-4 size-6 text-primary" aria-hidden="true" />
				<p class={label}>{CONTACTS.hours}</p>
				<p class={value}>{settings.work_hours}</p>
			</li>
		{/if}
	</ul>
	{#if settings.social_links.length > 0}
		<ul class="mt-6 flex flex-wrap gap-3">
			{#each settings.social_links as link (link.url)}
				<li>
					<a
						href={link.url}
						class="inline-flex rounded-full px-4 py-2 text-sm font-medium text-primary glass"
						rel="noopener external"
						target="_blank">{link.label}</a
					>
				</li>
			{/each}
		</ul>
	{/if}
	<div class="mt-8">
		<Button href="/lead" onclick={(event: MouseEvent) => openFromLink(event)}>
			{CONTACTS.cta}
			<ArrowUpRight
				class="transition-transform group-hover/button:translate-x-1 group-hover/button:-translate-y-1"
				aria-hidden="true"
			/>
		</Button>
	</div>
</Section>
