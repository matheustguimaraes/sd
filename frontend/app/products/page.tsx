"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { productsApi, Product } from "@/lib/api";
import { handleLogout } from "@/lib/auth";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function ProductsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: products, isLoading } = useQuery({
    queryKey: ["products"],
    queryFn: () => productsApi.list(),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => productsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
  });

  const handleDelete = async (id: number) => {
    if (confirm("Tem certeza que deseja excluir este produto?")) {
      deleteMutation.mutate(id);
    }
  };

  const handleLogoutClick = () => {
    handleLogout();
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg">Carregando produtos...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <h1 className="text-xl font-bold text-gray-900">Produtos</h1>
            <div className="flex gap-4">
              <Link
                href="/products/new"
                className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
              >
                Novo Produto
              </Link>
              <button
                onClick={handleLogoutClick}
                className="rounded-md bg-red-600 px-4 py-2 text-white hover:bg-red-700"
              >
                Sair
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {products && products.length === 0 ? (
          <div className="rounded-lg bg-white p-8 text-center shadow">
            <p className="text-gray-500">Nenhum produto encontrado.</p>
            <Link
              href="/products/new"
              className="mt-4 inline-block text-blue-600 hover:text-blue-800"
            >
              Criar primeiro produto
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {products?.map((product) => (
              <div
                key={product.id}
                className="overflow-hidden rounded-lg bg-white shadow"
              >
                {product.thumbnail_url ? (
                  <img
                    src={product.thumbnail_url}
                    alt={product.name}
                    className="h-48 w-full object-cover"
                  />
                ) : (
                  <div className="flex h-48 w-full items-center justify-center bg-gray-200">
                    <span className="text-gray-400">Sem imagem</span>
                  </div>
                )}
                <div className="p-4">
                  <h2 className="text-lg font-semibold text-gray-900">
                    {product.name}
                  </h2>
                  <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                    {product.description || "Sem descrição"}
                  </p>
                  <p className="mt-2 text-lg font-bold text-gray-900">
                    R$ {parseFloat(product.price).toFixed(2)}
                  </p>
                  <div className="mt-4 flex gap-2">
                    <Link
                      href={`/products/${product.id}`}
                      className="flex-1 rounded-md bg-blue-600 px-3 py-2 text-center text-sm text-white hover:bg-blue-700"
                    >
                      Ver
                    </Link>
                    <Link
                      href={`/products/${product.id}/edit`}
                      className="flex-1 rounded-md bg-yellow-600 px-3 py-2 text-center text-sm text-white hover:bg-yellow-700"
                    >
                      Editar
                    </Link>
                    <button
                      onClick={() => handleDelete(product.id)}
                      className="flex-1 rounded-md bg-red-600 px-3 py-2 text-sm text-white hover:bg-red-700"
                    >
                      Excluir
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
