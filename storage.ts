import { type User, type InsertUser } from "@shared/schema";
import { randomUUID } from "crypto";

export interface IStorage {
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
}

export class MemStorage implements IStorage {
  private users: Map<string, User> = new Map();
  async getUser(id: string)               { return this.users.get(id); }
  async getUserByUsername(username: string){ return [...this.users.values()].find(u => u.username === username); }
  async createUser(insertUser: InsertUser) {
    const id = randomUUID();
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }
}

export const storage = new MemStorage();