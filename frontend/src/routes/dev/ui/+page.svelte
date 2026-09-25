<script lang="ts">
	import { Alert } from '$lib/components/ui/alert';
	import { Button } from '$lib/components/ui/button';
	import { Checkbox } from '$lib/components/ui/checkbox';
	import { Container } from '$lib/components/ui/container';
	import * as Dialog from '$lib/components/ui/dialog';
	import { Field } from '$lib/components/ui/field';
	import { Input } from '$lib/components/ui/input';
	import { PhoneInput } from '$lib/components/ui/phone-input';
	import { ResponsiveImage } from '$lib/components/ui/responsive-image';
	import { Section } from '$lib/components/ui/section';
	import { Select } from '$lib/components/ui/select';
	import * as Sheet from '$lib/components/ui/sheet';
	import { Textarea } from '$lib/components/ui/textarea';
	import type { ImageAsset } from '$lib/types';

	let { form } = $props();

	const variants = ['default', 'secondary', 'outline', 'ghost', 'link'] as const;
	const sizes = ['sm', 'default', 'lg'] as const;
	const options = [
		{ value: 'kitchens', label: 'Кухни под заказ' },
		{ value: 'wardrobes', label: 'Шкафы' }
	];
	const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="400"><rect width="640" height="400" fill="#a07850"/></svg>`;
	const sample: ImageAsset = {
		url: `data:image/svg+xml;base64,${btoa(svg)}`,
		srcset: `data:image/svg+xml;base64,${btoa(svg)} 640w`,
		width: 640,
		height: 400,
		alt: 'Пример фото',
		color: '#a07850'
	};
</script>

<svelte:head>
	<title>UI kit | Фабрика Уюта</title>
	<meta name="robots" content="noindex" />
</svelte:head>

<Container class="space-y-16 pt-32 pb-24">
	<h1 class="text-5xl font-light text-primary">UI kit</h1>

	<section aria-labelledby="buttons" class="space-y-4">
		<h2 id="buttons" class="text-3xl text-primary">Button</h2>
		{#each sizes as size (size)}
			<div class="flex flex-wrap items-center gap-3">
				{#each variants as variant (variant)}
					<Button {variant} {size}>{variant} {size}</Button>
				{/each}
			</div>
		{/each}
		<div class="flex flex-wrap items-center gap-3">
			<Button disabled>disabled</Button>
			<Button loading>loading</Button>
			<Button href="/dev/ui">href</Button>
			<Button size="icon" variant="secondary" aria-label="Иконка">+</Button>
		</div>
	</section>

	<section aria-labelledby="fields" class="space-y-4">
		<h2 id="fields" class="text-3xl text-primary">Поля и форма</h2>
		<form method="POST" class="grid max-w-xl gap-7">
			<Field id="ui-name" label="Обычное поле" hint="Подсказка под полем">
				{#snippet children({ id, describedBy, invalid })}
					<Input {id} name="name" aria-describedby={describedBy} aria-invalid={invalid} />
				{/snippet}
			</Field>
			<Field id="ui-email" label="Поле с ошибкой" required error="Текст ошибки">
				{#snippet children({ id, describedBy, invalid })}
					<Input
						{id}
						name="email"
						type="email"
						aria-describedby={describedBy}
						aria-invalid={invalid}
					/>
				{/snippet}
			</Field>
			<Field id="ui-disabled" label="Отключено">
				{#snippet children({ id })}
					<Input {id} name="disabled" disabled value="Нельзя изменить" />
				{/snippet}
			</Field>
			<Field id="ui-phone" label="Телефон">
				{#snippet children({ id, describedBy, invalid })}
					<PhoneInput {id} name="phone" aria-describedby={describedBy} aria-invalid={invalid} />
				{/snippet}
			</Field>
			<Field id="ui-product" label="Выбор">
				{#snippet children({ id, describedBy, invalid })}
					<Select
						{id}
						name="product"
						{options}
						placeholder="Выберите"
						aria-describedby={describedBy}
						aria-invalid={invalid}
					/>
				{/snippet}
			</Field>
			<Field id="ui-comment" label="Многострочное поле">
				{#snippet children({ id, describedBy, invalid })}
					<Textarea {id} name="comment" aria-describedby={describedBy} aria-invalid={invalid} />
				{/snippet}
			</Field>
			<Field id="ui-consent" label="" error="Ошибка чекбокса">
				{#snippet children({ id, describedBy, invalid })}
					<Checkbox {id} name="consent" aria-describedby={describedBy} aria-invalid={invalid}>
						Согласен с <a href="/consent" class="text-primary underline">условиями</a>
					</Checkbox>
				{/snippet}
			</Field>
			<Button type="submit">Отправить</Button>
		</form>
		{#if form?.submitted}
			<Alert tone="success" title="Форма отправлена">
				<pre data-testid="submitted">{JSON.stringify(form.submitted)}</pre>
			</Alert>
		{/if}
	</section>

	<section aria-labelledby="alerts" class="space-y-4">
		<h2 id="alerts" class="text-3xl text-primary">Alert</h2>
		<Alert tone="success" title="Успех">Заявка принята.</Alert>
		<Alert tone="error" title="Ошибка">Не получилось отправить.</Alert>
		<Alert tone="info">Информационное сообщение.</Alert>
	</section>

	<section aria-labelledby="overlays" class="flex flex-wrap gap-3">
		<h2 id="overlays" class="w-full text-3xl text-primary">Dialog и Sheet</h2>
		<Dialog.Root>
			<Dialog.Trigger>
				{#snippet child({ props })}<Button variant="outline" {...props}>Открыть Dialog</Button
					>{/snippet}
			</Dialog.Trigger>
			<Dialog.Content>
				<Dialog.Header>
					<Dialog.Title>Заголовок диалога</Dialog.Title>
					<Dialog.Description>Описание диалога.</Dialog.Description>
				</Dialog.Header>
			</Dialog.Content>
		</Dialog.Root>
		<Sheet.Root>
			<Sheet.Trigger>
				{#snippet child({ props })}<Button variant="outline" {...props}>Открыть Sheet</Button
					>{/snippet}
			</Sheet.Trigger>
			<Sheet.Content side="right" class="p-6">
				<Sheet.Title>Панель</Sheet.Title>
			</Sheet.Content>
		</Sheet.Root>
	</section>

	<section aria-labelledby="images" class="grid gap-6 sm:grid-cols-2">
		<h2 id="images" class="text-3xl text-primary sm:col-span-2">ResponsiveImage</h2>
		<ResponsiveImage image={sample} sizes="50vw" class="w-full rounded-2xl" />
		<ResponsiveImage image={null} sizes="50vw" aspect="16/10" class="w-full rounded-2xl" />
	</section>
</Container>

<Section id="ui-section" title="Section default" subtitle="Надзаголовок">
	<p>Содержимое секции.</p>
</Section>
<Section title="Section muted" subtitle="Надзаголовок" tone="muted">
	<p>Содержимое секции.</p>
</Section>
<Section title="Section inverted" subtitle="Надзаголовок" tone="inverted">
	<p>Содержимое секции.</p>
</Section>
