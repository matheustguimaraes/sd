"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { productsApi } from "@/lib/api";
import Link from "next/link";
import { useState } from "react";

export default function ProductDetailPage() {
  const params = useParams();
  const router = useRouter();
  const productId = Number(params.id);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const queryClient = useQueryClient();

  const { data: product, isLoading } = useQuery({
    queryKey: ["product", productId],
    queryFn: () => productsApi.get(productId),
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => productsApi.uploadImage(productId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["product", productId] });
      queryClient.invalidateQueries({ queryKey: ["products"] });
      setSelectedFile(null);
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg">Carregando...</div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg">Produto não encontrado</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <h1 className="text-xl font-bold text-gray-900">{product.name}</h1>
            <div className="flex gap-4">
              <Link
                href="/products"
                className="rounded-md bg-gray-600 px-4 py-2 text-white hover:bg-gray-700"
              >
                Voltar
              </Link>
              <Link
                href={`/products/${productId}/edit`}
                className="rounded-md bg-yellow-600 px-4 py-2 text-white hover:bg-yellow-700"
              >
                Editar
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="rounded-lg bg-white p-8 shadow">
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
            <div>
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="w-full rounded-lg object-cover"
                />
              ) : (
                <div className="flex h-64 w-full items-center justify-center rounded-lg bg-gray-200">
                  <span className="text-gray-400">Sem imagem</span>
                </div>
              )}

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700">
                  Upload de Imagem
                </label>
                <div className="mt-2 flex gap-2">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:rounded-md file:border-0 file:bg-blue-50 file:px-4 file:py-2 file:text-blue-700 hover:file:bg-blue-100"
                  />
                  <button
                    onClick={handleUpload}
                    disabled={!selectedFile || uploadMutation.isPending}
                    className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
                  >
                    {uploadMutation.isPending ? "Enviando..." : "Enviar"}
                  </button>
                </div>
                {uploadMutation.isSuccess && (
                  <div className="mt-2 text-sm text-green-600">
                    Imagem enviada com sucesso! Processando...
                  </div>
                )}
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-gray-900">{product.name}</h2>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                R$ {parseFloat(product.price).toFixed(2)}
              </p>
              <div className="mt-4">
                <h3 className="text-lg font-semibold text-gray-700">Descrição</h3>
                <p className="mt-2 text-gray-600">
                  {product.description || "Sem descrição"}
                </p>
              </div>
              <div className="mt-4">
                <p className="text-sm text-gray-500">
                  Criado em: {new Date(product.created_at).toLocaleDateString("pt-BR")}
                </p>
                <p className="text-sm text-gray-500">
                  Atualizado em: {new Date(product.updated_at).toLocaleDateString("pt-BR")}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

