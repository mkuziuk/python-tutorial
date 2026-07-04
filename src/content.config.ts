import { defineCollection, z } from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

export const collections = {
  docs: defineCollection({
    loader: docsLoader(),
    schema: docsSchema({
      extend: z.object({
        concepts: z.array(z.string()).optional(),
        difficulty: z.string().optional(),
        projectId: z.string().optional(),
        time: z.string().optional(),
        concept: z.string().optional(),
        usedIn: z.array(z.string()).optional(),
        order: z.number().optional(),
      }),
    }),
  }),
};
