import { EntityType } from "@coderone/bomberland-library";
import { IWorldState } from "../Game/Entity/World/World";

export const mockWorldState: IWorldState = {
    units: [
        {
            coordinates: [5, 8],
            hp: 4,
            inventory: {
                bombs: 4,
            },
            blast_diameter: 4,
            invulnerability: 10,
            agent_id: "a",
            unit_id: "a",
        },
        {
            coordinates: [5, 5],
            hp: 3,
            inventory: {
                bombs: 3,
            },
            blast_diameter: 2,
            invulnerability: 0,
            agent_id: "b",
            unit_id: "b",
        },
    ],
    entities: [
        {
            x: 6,
            y: 1,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 3,
            y: 4,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 4,
            y: 5,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 0,
            y: 7,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 6,
            y: 3,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 1,
            y: 5,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 4,
            y: 6,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 3,
            y: 6,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 2,
            y: 6,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 7,
            y: 6,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 1,
            y: 2,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 1,
            y: 1,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 8,
            y: 7,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 4,
            y: 1,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 8,
            y: 5,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 4,
            y: 7,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 8,
            y: 6,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            x: 7,
            y: 7,
            type: EntityType.MetalBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 1,
            y: 6,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 7,
            y: 0,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 3,
            y: 2,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 0,
            y: 0,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 2,
            y: 3,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 1,
            y: 3,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 2,
            y: 4,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 0,
            y: 2,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 8,
            y: 8,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 7,
            y: 4,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 6,
            y: 7,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 5,
            y: 0,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 3,
            y: 8,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 2,
            y: 0,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 6,
            y: 2,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 0,
            y: 8,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 6,
            y: 6,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 1,
            y: 0,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 7,
            y: 3,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 1,
            x: 3,
            y: 1,
            type: EntityType.WoodBlock,
            created: 0,
        },
        {
            hp: 3,
            x: 1,
            y: 4,
            type: EntityType.OreBlock,
            created: 0,
        },
        {
            hp: 3,
            x: 1,
            y: 7,
            type: EntityType.OreBlock,
            created: 0,
        },
        {
            hp: 3,
            x: 5,
            y: 1,
            type: EntityType.OreBlock,
            created: 0,
        },
        {
            hp: 3,
            x: 5,
            y: 6,
            type: EntityType.OreBlock,
            created: 0,
        },
        {
            hp: 3,
            x: 7,
            y: 8,
            type: EntityType.OreBlock,
            created: 0,
        },
    ],
};
