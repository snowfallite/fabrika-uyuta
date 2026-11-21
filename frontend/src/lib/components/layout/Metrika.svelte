<script lang="ts">
	import { startMetrika } from './metrika';

	interface Props {
		/** Counter number from PUBLIC_YANDEX_METRIKA_ID; empty leaves the site without analytics. */
		id: string;
	}

	let { id }: Props = $props();

	const counter = $derived(Number(id));
	const enabled = $derived(id !== '' && Number.isInteger(counter) && counter > 0);

	$effect(() => {
		if (!enabled) return;
		return startMetrika(counter);
	});
</script>

{#if enabled}
	<noscript
		><div>
			<img src="https://mc.yandex.ru/watch/{counter}" class="absolute -left-[9999px]" alt="" />
		</div></noscript
	>
{/if}
