# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 09:35:48 2025
@author: aurel
"""
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import streamlit.runtime.scriptrunner as st_runner

# --- Keep the graph persistent ---
if "graph" not in st.session_state:
    st.session_state.graph = nx.Graph()

# --- Keep a history of relationships ---
if "relation_history" not in st.session_state:
    st.session_state.relation_history = []  # Liste pour stocker toutes les relations

# --- Page layout ---
st.set_page_config(layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
main > div.block-container {
    padding-top: 7rem !important;
}

/* 🔹 Colonne gauche (graph + historique) */
[data-testid="column"]:first-child {
    height: 100vh;
    background-color: #0a0a0a;
    border-right: 3px solid black;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    padding-bottom: 2rem;
}

.graph-container {
    flex: 3;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
}

.history-container {
    flex: 1;
    width: 90%;
    background-color: #111;
    border-radius: 10px;
    padding: 1rem;
    margin-top: 1rem;
    color: white;
    overflow-y: auto;
}

.delete-button {
    background-color: transparent;
    border: none;
    color: red;
    font-size: 18px;
    cursor: pointer;
    margin-left: 10px;
}
.delete-button:hover {
    color: #ff4444;
}

[data-testid="column"]:last-child {
    background-color: white;
    padding: 3rem !important;
    color: black;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

# --- Split page into two columns (2/3 and 1/3) ---
col_graph, col_text = st.columns([2, 1])

# --- LEFT COLUMN = GRAPH + HISTORY ---
with col_graph:
    G = st.session_state.graph

    # Couleurs selon le type de relation
    color_map = {
        "friendly relationship": "blue",
        "professional relationship": "green",
        "familial relationship": "red",
        "acquaintanceship": "orange",
        "romantic relationship": "yellow"
    }

    # --- Graph ---
    with st.container():
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        edge_colors = []
        for u, v, data in G.edges(data=True):
            rel_type = data.get("relation", "acquaintanceship")
            edge_colors.append(color_map.get(rel_type, "gray"))

        pos = nx.spring_layout(G, seed=42)
        nx.draw(
            G, pos,
            with_labels=True,
            node_color="black",
            font_color="white",
            node_size=600,
            font_size=10,
            edge_color=edge_colors,
            width=2,
            ax=ax
        )

        st.pyplot(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Historique des relations ---
    st.markdown('<div class="history-container">', unsafe_allow_html=True)
    st.subheader("Relation Historic")
    
    if st.session_state.relation_history:
        for i, (p1, rel, p2) in enumerate(reversed(st.session_state.relation_history)):
            color = color_map.get(rel, "gray")
    
            col1, col2 = st.columns([6, 1])  # colonne texte + colonne bouton
            with col1:
                st.markdown(
                    f"**{p1}** is in a <span style='color:{color}; font-weight:bold;'>{rel}</span> with **{p2}**.",
                    unsafe_allow_html=True
                )
            with col2:
                # Bouton de suppression (croix rouge)
                if st.button("❌", key=f"delete_{i}"):
                    st.session_state.to_delete = i  # stocke l'index de la relation à supprimer
    
            # ✅ Si la suppression est demandée pour cette ligne, afficher le bouton de confirmation juste en dessous
            if "to_delete" in st.session_state and st.session_state.to_delete == i:
                st.warning(f"Do you really want to delete the relation between {p1} and {p2}?")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Yes, delete", key=f"confirm_delete_{i}"):
                        try:
                            # Retirer la relation du graphe et de l’historique
                            st.session_state.graph.remove_edge(p1, p2)
                        except:
                            pass
                        # Supprimer de la liste d'historique
                        del st.session_state.relation_history[len(st.session_state.relation_history) - 1 - i]
                        del st.session_state.to_delete
                        st.rerun()
                with c2:
                    if st.button("Cancel", key=f"cancel_delete_{i}"):
                        del st.session_state.to_delete
                        st.rerun()
    
    else:
        st.write("No relationship has been added yet.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- RIGHT COLUMN = TEXT + INPUTS ---
with col_text:
    st.title("Welcome in your own network")
    st.write("In this webpage, you can create and model your personal relationship network.")
    st.write("To begin, write your name below, click **Add**, and watch the network grow!")

    # Add a person
    st.header("Add a person")
    with st.form("add_person_form"):
        name = st.text_input("Enter the person's name:")
        submitted = st.form_submit_button("Add")

    if submitted:
        if name:
            st.session_state.graph.add_node(name)
            st.success(f"{name} has been added to the network!")
        else:
            st.warning("Please enter a name before clicking Add.")

    st.markdown("---")

    # Add a relationship
    # Add a relationship
    st.header("Add a relationship")

    if len(st.session_state.graph.nodes) < 2:
        st.info("You need at least two people in the network to create a relationship.")
    else:
        people = list(st.session_state.graph.nodes)

        person1 = st.selectbox("Select the first person:", people, key="p1")
        relationship_type = st.selectbox(
            "Select the type of relationship:",
            ["friendly relationship", "professional relationship", "familial relationship","romantic relationship", "acquaintanceship"],
            key="rel_type"
        )
        
        # ✅ CHANGEMENT 1: Remplacer st.selectbox par st.multiselect
        # Notez que j'ai aussi changé le label pour être plus clair
        persons2_list = st.multiselect(
            "Select the second person (or several):", 
            people, 
            key="p2_multi" # J'ai changé la clé pour éviter les conflits
        )

        if st.button("Add relationship"):
            
            # ✅ CHANGEMENT 2: Logique de traitement de la liste
            if not persons2_list:
                st.warning("Please select at least one person for the relationship.")
            else:
                added_count = 0
                skipped_count = 0
                
                # On boucle sur toutes les personnes sélectionnées
                for person2 in persons2_list:
                    if person1 != person2:
                        # On ajoute l'arête et l'historique pour CHACUNE
                        st.session_state.graph.add_edge(person1, person2, relation=relationship_type)
                        st.session_state.relation_history.append((person1, relationship_type, person2))
                        added_count += 1
                    else:
                        # Si l'utilisateur s'est sélectionné lui-même dans la liste
                        skipped_count += 1

                # On affiche des messages de succès/d'avertissement clairs
                if added_count > 0:
                    st.success(f"{added_count} relationship(s) added for {person1}!")
                if skipped_count > 0:
                    st.warning("You cannot select yourself. That selection was skipped.")
    
    st.markdown("---")
    
    # --- Delete a person ---
    st.header("Delete a person")
    
    # On ne peut supprimer que s'il y a des personnes dans le réseau
    if len(st.session_state.graph.nodes) == 0:
        st.info("There is no one in the network to delete.")
    else:
        people = list(st.session_state.graph.nodes)
        
        # Clé pour suivre la personne sélectionnée pour la suppression
        person_key = "person_to_delete_select"
        
        person_to_delete = st.selectbox(
            "Select the person to delete:",
            people,
            key=person_key
        )
    
        # Initialiser l'état de confirmation s'il n'existe pas
        if "confirm_delete_person" not in st.session_state:
            st.session_state.confirm_delete_person = None
    
        # Bouton principal pour INITIALLOC la suppression
        if st.button("Delete this person"):
            # On stocke la personne qui doit être confirmée
            st.session_state.confirm_delete_person = person_to_delete
            # Pas besoin de rerun ici, le script continue et affiche le bloc de confirmation
    
        # --- Bloc de Confirmation ---
        # S'affiche SEULEMENT si la personne à confirmer est la même que celle sélectionnée
        if st.session_state.confirm_delete_person == person_to_delete and person_to_delete is not None:
            
            st.warning(f"Do you really want to delete **{person_to_delete}**? This will remove them and ALL their relationships permanently.")
            
            c1, c2 = st.columns(2)
            with c1:
                # OUI, supprimer
                if st.button("Yes, delete permanently", key="confirm_del_btn"):
                    name_to_remove = st.session_state.confirm_delete_person
                    
                    # 1. Supprimer le nœud du graphe (NetworkX)
                    # (Cela supprime aussi automatiquement toutes les arêtes connectées à ce nœud)
                    try:
                        st.session_state.graph.remove_node(name_to_remove)
                    except Exception as e:
                        st.error(f"Error removing node: {e}")
    
                    # 2. Nettoyer l'historique (st.session_state.relation_history)
                    # On reconstruit une nouvelle liste SANS les relations impliquant cette personne
                    current_history = st.session_state.relation_history
                    new_history = [
                        (p1, rel, p2) for (p1, rel, p2) in current_history
                        if p1 != name_to_remove and p2 != name_to_remove
                    ]
                    st.session_state.relation_history = new_history
                    
                    # 3. Réinitialiser l'état de confirmation et rafraîchir
                    st.session_state.confirm_delete_person = None
                    st.success(f"{name_to_remove} and all their relationships have been removed.")
                    st.rerun()
    
            with c2:
                # NON, annuler
                if st.button("Cancel", key="cancel_del_btn"):
                    st.session_state.confirm_delete_person = None
                    st.rerun()
